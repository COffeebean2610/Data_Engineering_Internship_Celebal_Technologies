"""Schema and integrity tests for the production SQLite database."""

from __future__ import annotations

import sqlite3
import unittest

from scripts.database_manager import DATABASE_PATH, database_connection


class DatabaseTests(unittest.TestCase):
    """Verify database availability, schema contracts, and integrity rules."""

    def test_database_file_exists(self) -> None:
        self.assertTrue(DATABASE_PATH.exists())

    def test_connection_is_available(self) -> None:
        with database_connection() as connection:
            self.assertEqual(connection.execute("SELECT 1").fetchone()[0], 1)

    def test_expected_tables_exist(self) -> None:
        with database_connection() as connection:
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        self.assertTrue({"customers", "products", "orders", "order_items"}.issubset(tables))

    def test_primary_key_columns_exist(self) -> None:
        expected = {"customers": "customer_id", "products": "product_id", "orders": "order_id", "order_items": "item_id"}
        with database_connection() as connection:
            for table, key in expected.items():
                primary_keys = {row[1] for row in connection.execute(f"PRAGMA table_info({table})") if row[5]}
                self.assertIn(key, primary_keys)

    def test_foreign_key_definitions_exist(self) -> None:
        with database_connection() as connection:
            order_fks = connection.execute("PRAGMA foreign_key_list(orders)").fetchall()
            item_fks = connection.execute("PRAGMA foreign_key_list(order_items)").fetchall()
        self.assertEqual(len(order_fks), 1)
        self.assertEqual(len(item_fks), 2)

    def test_referential_integrity_is_clean(self) -> None:
        with database_connection() as connection:
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_required_indexes_exist(self) -> None:
        with database_connection() as connection:
            indexes = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'index'")}
        self.assertTrue({"idx_orders_customer_id", "idx_orders_order_date", "idx_products_category"}.issubset(indexes))

    def test_record_counts_are_positive(self) -> None:
        with database_connection() as connection:
            for table in ("customers", "products", "orders", "order_items"):
                self.assertGreater(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], 0)

    def test_no_duplicate_primary_keys(self) -> None:
        with database_connection() as connection:
            checks = (("customers", "customer_id"), ("products", "product_id"), ("orders", "order_id"), ("order_items", "item_id"))
            for table, key in checks:
                duplicates = connection.execute(f"SELECT COUNT(*) FROM (SELECT {key} FROM {table} GROUP BY {key} HAVING COUNT(*) > 1)").fetchone()[0]
                self.assertEqual(duplicates, 0, table)

    def test_required_not_null_values_are_present(self) -> None:
        with database_connection() as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM customers WHERE customer_name IS NULL").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM orders WHERE order_date IS NULL").fetchone()[0], 0)

    def test_integrity_check_is_ok(self) -> None:
        with sqlite3.connect(DATABASE_PATH) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
