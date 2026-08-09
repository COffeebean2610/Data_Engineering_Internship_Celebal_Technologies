"""Validation tests for cleaned source datasets."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLEANED = ROOT / "data" / "cleaned"


class DataValidationTests(unittest.TestCase):
    """Ensure cleaned CSV values comply with database-ready expectations."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.customers = pd.read_csv(CLEANED / "customers_clean.csv")
        cls.products = pd.read_csv(CLEANED / "products_clean.csv")
        cls.orders = pd.read_csv(CLEANED / "orders_clean.csv")
        cls.items = pd.read_csv(CLEANED / "order_items_clean.csv")

    def test_customer_ids_are_unique(self) -> None:
        self.assertFalse(self.customers["customer_id"].duplicated().any())

    def test_product_ids_are_unique(self) -> None:
        self.assertFalse(self.products["product_id"].duplicated().any())

    def test_order_item_ids_are_unique(self) -> None:
        self.assertFalse(self.items["item_id"].duplicated().any())

    def test_valid_customer_emails_match_pattern(self) -> None:
        valid = self.customers[self.customers["email_valid"].astype(bool)]
        pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        self.assertTrue(valid["email"].map(lambda value: bool(pattern.fullmatch(str(value)))).all())

    def test_order_dates_are_parseable(self) -> None:
        self.assertFalse(pd.to_datetime(self.orders["order_date"], errors="coerce").isna().any())

    def test_product_prices_are_non_negative(self) -> None:
        self.assertTrue((self.products[["cost_price", "selling_price"]] >= 0).all().all())

    def test_stock_quantities_are_non_negative(self) -> None:
        self.assertTrue((self.products["stock_quantity"] >= 0).all())

    def test_discounts_are_in_valid_range(self) -> None:
        self.assertTrue(self.items["discount_percent"].between(0, 100).all())

    def test_quantities_are_positive(self) -> None:
        self.assertTrue((self.items["quantity"] > 0).all())

    def test_required_source_files_are_non_empty(self) -> None:
        for path in CLEANED.glob("*_clean.csv"):
            self.assertGreater(path.stat().st_size, 0, path.name)
