"""Load cleaned CSV data into SQLite and create an integrity loading report."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any

import pandas as pd

from scripts.create_database import create_database
from scripts.database_utils import DATABASE_PATH, OUTPUT_DIR, get_connection, validation_results, write_loading_report

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "cleaned"
TABLE_COLUMNS = {
    "customers": ["customer_id", "customer_name", "email", "phone", "city", "state", "country", "registration_date", "customer_type"],
    "products": ["product_id", "product_name", "category", "subcategory", "brand", "cost_price", "selling_price", "stock_quantity", "profit_margin"],
    "orders": ["order_id", "customer_id", "order_date", "status", "region_code", "payment_method"],
    "order_items": ["item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"],
}
SOURCE_FILES = {table: DATA_DIR / f"{table}_clean.csv" for table in TABLE_COLUMNS}


def _read_source(table: str) -> pd.DataFrame:
    """Read and select only columns represented in the database schema."""
    path = SOURCE_FILES[table]
    if not path.exists():
        raise FileNotFoundError(f"Cleaned source file is missing: {path}")
    frame = pd.read_csv(path)
    missing = set(TABLE_COLUMNS[table]) - set(frame.columns)
    if missing:
        raise ValueError(f"{path.name} is missing expected columns: {sorted(missing)}")
    return frame[TABLE_COLUMNS[table]].where(pd.notna(frame[TABLE_COLUMNS[table]]), None)


def _valid_rows(table: str, frame: pd.DataFrame, connection: sqlite3.Connection) -> tuple[list[tuple[Any, ...]], int]:
    """Pre-filter FK and enum issues so rejected records are counted, not silently lost."""
    valid_customer_ids = {row[0] for row in connection.execute("SELECT customer_id FROM customers")}
    valid_order_ids = {row[0] for row in connection.execute("SELECT order_id FROM orders")}
    valid_product_ids = {row[0] for row in connection.execute("SELECT product_id FROM products")}
    rows: list[tuple[Any, ...]] = []
    rejected = 0
    for record in frame.itertuples(index=False, name=None):
        values = tuple(record)
        if table == "orders" and values[1] is not None and values[1] not in valid_customer_ids:
            rejected += 1
        elif table == "orders" and values[3] not in {"PLACED", "SHIPPED", "DELIVERED", "RETURNED", "CANCELLED"}:
            rejected += 1
        elif table == "order_items" and (values[1] not in valid_order_ids or values[2] not in valid_product_ids):
            rejected += 1
        else:
            rows.append(values)
    return rows, rejected


def _load_table(connection: sqlite3.Connection, table: str) -> tuple[int, int, int]:
    """Insert one table in a transaction using executemany and row-level fallback."""
    frame = _read_source(table)
    rows, rejected = _valid_rows(table, frame, connection)
    columns = TABLE_COLUMNS[table]
    statement = f"INSERT OR IGNORE INTO {table} ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})"
    before = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    try:
        connection.executemany(statement, rows)
    except sqlite3.DatabaseError:
        # A bad source row cannot roll back the whole table: retry valid rows singly.
        connection.rollback()
        for row in rows:
            try:
                connection.execute(statement, row)
            except sqlite3.DatabaseError:
                rejected += 1
    after = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    inserted = after - before
    failed = len(rows) - inserted
    return inserted, failed, rejected


def load_database() -> dict[str, Any]:
    """Rebuild, load, validate, and report on the complete SQLite database."""
    started = time.perf_counter()
    create_database()
    inserted: dict[str, int] = {}
    failed_rows = rejected_rows = 0
    with get_connection(DATABASE_PATH) as connection:
        for table in TABLE_COLUMNS:
            count, failed, rejected = _load_table(connection, table)
            inserted[table] = count
            failed_rows += failed
            rejected_rows += rejected
        validation = validation_results(connection)
        index_count = connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE type = 'index' AND name LIKE 'idx_%'").fetchone()[0]
    report = {
        "database_path": DATABASE_PATH,
        "rows_inserted": inserted,
        "failed_rows": failed_rows,
        "rejected_rows": rejected_rows,
        "validation": validation,
        "index_count": index_count,
        "execution_seconds": time.perf_counter() - started,
        "database_size_bytes": DATABASE_PATH.stat().st_size,
        "is_valid": not any(validation[key] for key in ("foreign_key_errors", "broken_order_customers", "broken_item_orders", "broken_item_products", "invalid_prices", "negative_or_zero_quantities", "invalid_discounts")),
    }
    write_loading_report(report, OUTPUT_DIR / "database_loading_report.txt")
    print_database_summary(report)
    return report


def print_database_summary(report: dict[str, Any]) -> None:
    """Print the requested professional completion summary."""
    rows = report["rows_inserted"]
    validation = report["validation"]
    print("\n====================================================")
    print("DATABASE CREATION SUMMARY")
    print("====================================================")
    print(f"Database Created      {DATABASE_PATH.name}")
    print("Tables Created       4")
    print(f"Indexes Created      {report['index_count']}")
    print(f"Customers Loaded     {rows['customers']}")
    print(f"Products Loaded      {rows['products']}")
    print(f"Orders Loaded        {rows['orders']}")
    print(f"Order Items Loaded   {rows['order_items']}")
    print(f"Foreign Key Errors   {validation['foreign_key_errors']}")
    print(f"Constraint Violations {report['failed_rows']}")
    print(f"Execution Time       {report['execution_seconds']:.2f} sec")
    print("Database Ready for Analytics" if report["is_valid"] else "Database validation requires attention")
    print("====================================================")


if __name__ == "__main__":
    load_database()
