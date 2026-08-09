"""Functions for validation reporting and summary generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.utils import OUTPUT_DIR, LOGGER


def generate_cleaning_report(report: dict[str, object], output_path: Path) -> None:
    """Write the detailed cleaning report as plain text."""
    lines = [
        "========================================",
        "DATA CLEANING REPORT",
        "========================================",
        "",
        f"Customers Loaded: {report.get('customers_loaded', 0)}",
        f"Customers Cleaned: {report.get('customers_cleaned', 0)}",
        f"Duplicate Customers Removed: {report.get('duplicate_customers_removed', 0)}",
        f"Invalid Emails Corrected: {report.get('invalid_emails_corrected', 0)}",
        f"Missing Phone Numbers Fixed: {report.get('missing_phone_fixed', 0)}",
        "",
        f"Products Loaded: {report.get('products_loaded', 0)}",
        f"Products Cleaned: {report.get('products_cleaned', 0)}",
        f"Duplicate Products Removed: {report.get('duplicate_products_removed', 0)}",
        f"Negative Stock Fixed: {report.get('negative_stock_fixed', 0)}",
        f"Price Validation Fixes: {report.get('price_validation_fixes', 0)}",
        "",
        f"Orders Loaded: {report.get('orders_loaded', 0)}",
        f"Orders Cleaned: {report.get('orders_cleaned', 0)}",
        f"Wrong Date Formats Fixed: {report.get('wrong_date_formats_fixed', 0)}",
        f"Future Dates Corrected: {report.get('future_dates_corrected', 0)}",
        f"Null Customer IDs Preserved: {report.get('null_customer_ids_preserved', 0)}",
        "",
        f"Order Items Loaded: {report.get('order_items_loaded', 0)}",
        f"Order Items Cleaned: {report.get('order_items_cleaned', 0)}",
        f"Negative Quantities Fixed: {report.get('negative_quantities_fixed', 0)}",
        f"Discount Errors Fixed: {report.get('discount_errors_fixed', 0)}",
        f"Missing Product IDs: {report.get('missing_product_ids', 0)}",
        f"Missing Order IDs: {report.get('missing_order_ids', 0)}",
        "",
        f"Referential Integrity Issues: {report.get('referential_integrity_issues', 0)}",
        "",
        "========================================",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")
    LOGGER.info("Cleaning report written to %s", output_path)


def create_summary_dataframe(report: dict[str, object]) -> pd.DataFrame:
    """Create a one-row summary DataFrame for export."""
    summary = pd.DataFrame(
        [
            {
                "customers_loaded": report.get("customers_loaded", 0),
                "customers_cleaned": report.get("customers_cleaned", 0),
                "duplicate_customers_removed": report.get("duplicate_customers_removed", 0),
                "invalid_emails_corrected": report.get("invalid_emails_corrected", 0),
                "missing_phone_fixed": report.get("missing_phone_fixed", 0),
                "products_loaded": report.get("products_loaded", 0),
                "products_cleaned": report.get("products_cleaned", 0),
                "duplicate_products_removed": report.get("duplicate_products_removed", 0),
                "negative_stock_fixed": report.get("negative_stock_fixed", 0),
                "price_validation_fixes": report.get("price_validation_fixes", 0),
                "orders_loaded": report.get("orders_loaded", 0),
                "orders_cleaned": report.get("orders_cleaned", 0),
                "wrong_date_formats_fixed": report.get("wrong_date_formats_fixed", 0),
                "future_dates_corrected": report.get("future_dates_corrected", 0),
                "null_customer_ids_preserved": report.get("null_customer_ids_preserved", 0),
                "order_items_loaded": report.get("order_items_loaded", 0),
                "order_items_cleaned": report.get("order_items_cleaned", 0),
                "negative_quantities_fixed": report.get("negative_quantities_fixed", 0),
                "discount_errors_fixed": report.get("discount_errors_fixed", 0),
                "missing_product_ids": report.get("missing_product_ids", 0),
                "missing_order_ids": report.get("missing_order_ids", 0),
                "referential_integrity_issues": report.get("referential_integrity_issues", 0),
            }
        ]
    )
    return summary


def print_terminal_summary(report: dict[str, object]) -> None:
    """Display a formatted terminal summary for the user."""
    print("\n")
    print("========================================")
    print("DATA CLEANING SUMMARY")
    print("========================================")
    print(f"Customers Loaded : {report.get('customers_loaded', 0)}")
    print(f"Customers Cleaned : {report.get('customers_cleaned', 0)}")
    print(f"Duplicate Customers Removed : {report.get('duplicate_customers_removed', 0)}")
    print()
    print(f"Products Loaded : {report.get('products_loaded', 0)}")
    print(f"Products Cleaned : {report.get('products_cleaned', 0)}")
    print(f"Duplicate Products Removed : {report.get('duplicate_products_removed', 0)}")
    print()
    print(f"Orders Loaded : {report.get('orders_loaded', 0)}")
    print(f"Orders Cleaned : {report.get('orders_cleaned', 0)}")
    print(f"Future Dates Corrected : {report.get('future_dates_corrected', 0)}")
    print(f"Wrong Date Formats Fixed : {report.get('wrong_date_formats_fixed', 0)}")
    print()
    print(f"Order Items Loaded : {report.get('order_items_loaded', 0)}")
    print(f"Order Items Cleaned : {report.get('order_items_cleaned', 0)}")
    print(f"Negative Quantities Fixed : {report.get('negative_quantities_fixed', 0)}")
    print(f"Discount Errors Fixed : {report.get('discount_errors_fixed', 0)}")
    print(f"Missing Product IDs : {report.get('missing_product_ids', 0)}")
    print(f"Missing Order IDs : {report.get('missing_order_ids', 0)}")
    print()
    print("Cleaning Completed Successfully")
    print("========================================")


def save_invalid_email_report(invalid_emails_df: pd.DataFrame) -> Path:
    """Save invalid email rows to a CSV report in the output directory."""
    path = OUTPUT_DIR / "invalid_emails_report.csv"
    invalid_emails_df.to_csv(path, index=False)
    LOGGER.info("Saved invalid email report to %s", path)
    return path
