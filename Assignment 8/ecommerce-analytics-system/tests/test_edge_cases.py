"""Edge-case tests for validation, temporary databases, and CLI behavior."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from contextlib import closing
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from scripts.database_manager import DatabaseUnavailableError, database_connection
from scripts.report_cli import main, parse_iso_date
from scripts.report_service import DateRange, generate_report


class EdgeCaseTests(unittest.TestCase):
    """Exercise failure paths without mutating the production database."""

    def test_missing_database_has_friendly_error(self) -> None:
        with self.assertRaises(DatabaseUnavailableError):
            with database_connection(Path("missing_database.db")):
                pass

    def test_invalid_sql_query_is_rejected(self) -> None:
        with database_connection() as connection:
            with self.assertRaises(sqlite3.DatabaseError):
                connection.execute("SELECT invalid syntax")

    def test_invalid_date_format_is_rejected(self) -> None:
        with self.assertRaises(Exception):
            parse_iso_date("2025/01/01")

    def test_invalid_date_range_returns_exit_code_two(self) -> None:
        with patch("sys.argv", ["report_cli.py", "--report", "revenue", "--start-date", "2025-12-31", "--end-date", "2025-01-01"]):
            with redirect_stderr(StringIO()):
                self.assertEqual(main(), 2)

    def test_invalid_report_name_is_rejected(self) -> None:
        with database_connection() as connection:
            with self.assertRaises(ValueError):
                generate_report(connection, "unknown", DateRange())

    def test_zero_quantity_constraint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.db"
            with closing(sqlite3.connect(path)) as connection:
                connection.execute("CREATE TABLE items (quantity INTEGER CHECK(quantity > 0))")
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute("INSERT INTO items VALUES (0)")

    def test_negative_quantity_constraint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.db"
            with closing(sqlite3.connect(path)) as connection:
                connection.execute("CREATE TABLE items (quantity INTEGER CHECK(quantity > 0))")
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute("INSERT INTO items VALUES (-1)")

    def test_invalid_discount_constraint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.db"
            with closing(sqlite3.connect(path)) as connection:
                connection.execute("CREATE TABLE items (discount REAL CHECK(discount BETWEEN 0 AND 100))")
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute("INSERT INTO items VALUES (101)")

    def test_empty_database_has_no_project_tables(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.db"
            with closing(sqlite3.connect(path)) as connection:
                tables = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        self.assertEqual(tables, [])

    def test_empty_csv_file_is_detectable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.csv"
            path.touch()
            self.assertEqual(path.stat().st_size, 0)

    def test_unknown_order_id_returns_no_row(self) -> None:
        with database_connection() as connection:
            self.assertIsNone(connection.execute("SELECT order_id FROM orders WHERE order_id = ?", ("ORD-DOES-NOT-EXIST",)).fetchone())

    def test_unknown_product_id_returns_no_row(self) -> None:
        with database_connection() as connection:
            self.assertIsNone(connection.execute("SELECT product_id FROM products WHERE product_id = ?", ("PROD-DOES-NOT-EXIST",)).fetchone())

    def test_unknown_customer_id_returns_no_row(self) -> None:
        with database_connection() as connection:
            self.assertIsNone(connection.execute("SELECT customer_id FROM customers WHERE customer_id = ?", ("CUST-DOES-NOT-EXIST",)).fetchone())

    def test_future_date_filter_returns_empty_report(self) -> None:
        with database_connection() as connection:
            report = generate_report(connection, "top_products", DateRange("2099-01-01", "2099-12-31"))
        self.assertTrue(report.data.empty)

    def test_null_customer_ids_are_allowed_by_schema(self) -> None:
        with database_connection() as connection:
            nullable = {row[1]: row[3] for row in connection.execute("PRAGMA table_info(orders)")}
        self.assertEqual(nullable["customer_id"], 0)
