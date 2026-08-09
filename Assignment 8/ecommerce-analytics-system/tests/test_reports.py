"""Tests for report service execution and export behavior."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.database_manager import database_connection
from scripts.report_cli import export_report
from scripts.report_service import DateRange, available_reports, generate_report


class ReportTests(unittest.TestCase):
    """Verify every supported report executes without SQL failures."""

    def test_expected_reports_are_registered(self) -> None:
        expected = {"revenue", "customers", "products", "monthly_sales", "top_customers", "top_products", "retention", "segmentation", "category", "region"}
        self.assertTrue(expected.issubset(set(available_reports())))

    def test_every_registered_report_executes(self) -> None:
        with database_connection() as connection:
            for name in available_reports():
                result = generate_report(connection, name, DateRange())
                self.assertIsNotNone(result.data, name)

    def test_revenue_report_has_kpis(self) -> None:
        with database_connection() as connection:
            result = generate_report(connection, "revenue", DateRange())
        self.assertIn("total_revenue", result.data.columns)
        self.assertIn("top_customer", result.highlights)

    def test_date_filtered_monthly_sales_executes(self) -> None:
        with database_connection() as connection:
            result = generate_report(connection, "monthly_sales", DateRange("2025-01-01", "2025-12-31"))
        self.assertLessEqual(len(result.data), 12)

    def test_csv_and_text_export(self) -> None:
        with database_connection() as connection:
            result = generate_report(connection, "top_products", DateRange())
        with tempfile.TemporaryDirectory() as temporary_directory:
            original = __import__("scripts.report_cli", fromlist=["OUTPUT_DIR"]).OUTPUT_DIR
            module = __import__("scripts.report_cli", fromlist=["OUTPUT_DIR"])
            module.OUTPUT_DIR = Path(temporary_directory)
            try:
                csv_path, text_path = export_report("top_products", result.data)
            finally:
                module.OUTPUT_DIR = original
            self.assertTrue(csv_path.exists())
            self.assertTrue(text_path.exists())

    def test_empty_date_range_returns_a_valid_frame(self) -> None:
        with database_connection() as connection:
            result = generate_report(connection, "top_customers", DateRange("1900-01-01", "1900-01-02"))
        self.assertTrue(result.data.empty)
