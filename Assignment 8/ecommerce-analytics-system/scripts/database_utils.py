"""Reusable SQLite helpers, validation queries, and database report generation."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "ecommerce.db"
SQL_DIR = PROJECT_ROOT / "sql"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGGER = logging.getLogger("ecommerce_analytics.database")


def ensure_database_directories() -> None:
    """Create paths required by the database phase."""
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_connection(database_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Open a SQLite connection with foreign-key enforcement enabled."""
    ensure_database_directories()
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def execute_sql_file(connection: sqlite3.Connection, sql_path: Path) -> None:
    """Execute an SQL script atomically from a UTF-8 file."""
    if not sql_path.exists():
        raise FileNotFoundError(f"Required SQL file is missing: {sql_path}")
    connection.executescript(sql_path.read_text(encoding="utf-8"))


def validation_results(connection: sqlite3.Connection) -> dict[str, Any]:
    """Run integrity and analytics sanity checks and return scalar results."""
    queries = {
        "total_customers": "SELECT COUNT(*) FROM customers",
        "total_products": "SELECT COUNT(*) FROM products",
        "total_orders": "SELECT COUNT(*) FROM orders",
        "total_order_items": "SELECT COUNT(*) FROM order_items",
        "null_customer_names": "SELECT COUNT(*) FROM customers WHERE customer_name IS NULL",
        "null_order_dates": "SELECT COUNT(*) FROM orders WHERE order_date IS NULL",
        "duplicate_customer_ids": "SELECT COUNT(*) FROM (SELECT customer_id FROM customers GROUP BY customer_id HAVING COUNT(*) > 1)",
        "duplicate_order_ids": "SELECT COUNT(*) FROM (SELECT order_id FROM orders GROUP BY order_id HAVING COUNT(*) > 1)",
        "duplicate_emails": "SELECT COUNT(*) FROM (SELECT email FROM customers WHERE email IS NOT NULL GROUP BY email HAVING COUNT(*) > 1)",
        "broken_order_customers": "SELECT COUNT(*) FROM orders o LEFT JOIN customers c ON c.customer_id = o.customer_id WHERE o.customer_id IS NOT NULL AND c.customer_id IS NULL",
        "broken_item_orders": "SELECT COUNT(*) FROM order_items i LEFT JOIN orders o ON o.order_id = i.order_id WHERE o.order_id IS NULL",
        "broken_item_products": "SELECT COUNT(*) FROM order_items i LEFT JOIN products p ON p.product_id = i.product_id WHERE p.product_id IS NULL",
        "invalid_prices": "SELECT COUNT(*) FROM products WHERE cost_price < 0 OR selling_price < 0 UNION ALL SELECT COUNT(*) FROM order_items WHERE unit_price < 0",
        "negative_or_zero_quantities": "SELECT COUNT(*) FROM order_items WHERE quantity <= 0",
        "invalid_discounts": "SELECT COUNT(*) FROM order_items WHERE discount_percent NOT BETWEEN 0 AND 100",
        # Order dates are business dates; compare local calendar dates to avoid
        # false positives near midnight when SQLite's UTC clock is a day behind.
        "future_order_dates": "SELECT COUNT(*) FROM orders WHERE date(order_date) > date('now', 'localtime')",
        "foreign_key_errors": "SELECT COUNT(*) FROM pragma_foreign_key_check",
        "revenue": "SELECT COALESCE(ROUND(SUM(quantity * unit_price * (1 - discount_percent / 100.0)), 2), 0) FROM order_items",
    }
    return {name: connection.execute(query).fetchone()[0] for name, query in queries.items()}


def write_loading_report(report: dict[str, Any], output_path: Path) -> None:
    """Persist a readable, auditable database loading report."""
    lines = [
        "====================================================",
        "DATABASE LOADING REPORT",
        "====================================================",
        "",
        f"Database created successfully: {report['database_path']}",
        "Tables created: 4",
        "Constraints applied: primary keys, foreign keys, NOT NULL, UNIQUE, CHECK, date triggers",
        f"Indexes created: {report['index_count']}",
        "",
        "Rows inserted:",
        *[f"  {name}: {count}" for name, count in report["rows_inserted"].items()],
        f"Failed rows: {report['failed_rows']}",
        f"Rejected rows: {report['rejected_rows']}",
        "",
        "Validation results:",
        *[f"  {name}: {value}" for name, value in report["validation"].items()],
        "",
        f"Execution time: {report['execution_seconds']:.2f} sec",
        f"Database size: {report['database_size_bytes']:,} bytes",
        "Database ready for analytics: " + ("Yes" if report["is_valid"] else "No"),
        "====================================================",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")
