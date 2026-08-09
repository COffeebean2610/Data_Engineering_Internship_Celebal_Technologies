"""Cleaning pipeline for raw e-commerce CSV datasets."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.utils import (
    CLEANED_DATA_DIR,
    OUTPUT_DIR,
    RAW_DATA_DIR,
    LOGGER,
    clean_text,
    ensure_directories,
    load_csv_with_checks,
    normalize_category,
    parse_datetime,
    safe_numeric,
    validate_email,
)
from scripts.validation import (
    create_summary_dataframe,
    generate_cleaning_report,
    print_terminal_summary,
    save_invalid_email_report,
)


def load_raw_datasets() -> dict[str, pd.DataFrame]:
    """Load all four raw CSV files with validation checks."""
    ensure_directories()

    dataset_map = {
        "customers": RAW_DATA_DIR / "customers.csv",
        "products": RAW_DATA_DIR / "products.csv",
        "orders": RAW_DATA_DIR / "orders.csv",
        "order_items": RAW_DATA_DIR / "order_items.csv",
    }

    loaded: dict[str, pd.DataFrame] = {}
    for name, path in dataset_map.items():
        try:
            if name == "customers":
                df = load_csv_with_checks(
                    path,
                    expected_columns=[
                        "customer_id",
                        "customer_name",
                        "email",
                        "phone",
                        "city",
                        "state",
                        "country",
                        "registration_date",
                        "customer_type",
                    ],
                )
            elif name == "products":
                df = load_csv_with_checks(
                    path,
                    expected_columns=[
                        "product_id",
                        "product_name",
                        "category",
                        "subcategory",
                        "brand",
                        "cost_price",
                        "selling_price",
                        "stock_quantity",
                    ],
                )
            elif name == "orders":
                df = load_csv_with_checks(
                    path,
                    expected_columns=[
                        "order_id",
                        "customer_id",
                        "order_date",
                        "status",
                        "region_code",
                        "payment_method",
                    ],
                )
            else:
                df = load_csv_with_checks(
                    path,
                    expected_columns=["item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"],
                )

            loaded[name] = df
            LOGGER.info("Loaded %s rows from %s", len(df), path)
        except (FileNotFoundError, ValueError, UnicodeDecodeError) as exc:
            LOGGER.error("Unable to load %s: %s", name, exc)
            raise

    return loaded


def clean_customers(customers_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int | pd.DataFrame]]:
    """Normalize customers and report invalid email records."""
    df = customers_df.copy()
    metrics: dict[str, int | pd.DataFrame] = {}

    df.columns = [str(column).strip() for column in df.columns]
    before = len(df)

    df = df.drop_duplicates(subset=["customer_id", "customer_name", "email", "phone"], keep="first").copy()
    metrics["duplicate_customers_removed"] = before - len(df)

    df["customer_name"] = df["customer_name"].apply(lambda value: clean_text(value).title())
    df["city"] = df["city"].apply(clean_text)
    df["state"] = df["state"].apply(clean_text)
    df["country"] = df["country"].apply(clean_text)
    df["customer_type"] = df["customer_type"].fillna("REGULAR").astype(str).str.strip().str.upper()
    df["email"] = df["email"].apply(lambda value: str(value).strip().lower() if not pd.isna(value) else "")
    df["phone"] = df["phone"].apply(lambda value: "Not Available" if pd.isna(value) or str(value).strip() == "" else str(value).strip())

    df["email_valid"] = df["email"].apply(validate_email)

    invalid_email_df = df.loc[~df["email_valid"], ["customer_id", "email"]].copy()
    metrics["invalid_emails_report"] = invalid_email_df
    metrics["invalid_emails_corrected"] = int(len(invalid_email_df))
    metrics["missing_phone_fixed"] = int((customers_df["phone"].isna() | customers_df["phone"].astype(str).str.strip().eq("")).sum())

    LOGGER.info("Removed %s duplicate customers", metrics["duplicate_customers_removed"])
    LOGGER.info("Corrected %s invalid emails", metrics["invalid_emails_corrected"])
    LOGGER.info("Fixed %s missing phone values", metrics["missing_phone_fixed"])

    return df, metrics


def clean_products(products_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Normalize products, fix stock and price issues, and compute margin."""
    df = products_df.copy()
    metrics: dict[str, int] = {}

    df.columns = [str(column).strip() for column in df.columns]
    before = len(df)
    df = df.drop_duplicates(subset=["product_id", "product_name", "category", "subcategory", "brand"], keep="first").copy()
    metrics["duplicate_products_removed"] = before - len(df)

    df["product_name"] = df["product_name"].apply(lambda value: clean_text(value).title())
    df["category"] = df["category"].apply(normalize_category)
    df["subcategory"] = df["subcategory"].apply(normalize_category)
    df["brand"] = df["brand"].apply(lambda value: clean_text(value).title())

    df["cost_price"] = df["cost_price"].apply(lambda value: safe_numeric(value, 0.0))
    df["selling_price"] = df["selling_price"].apply(lambda value: safe_numeric(value, 0.0))
    df["stock_quantity"] = df["stock_quantity"].apply(lambda value: safe_numeric(value, 0.0))

    negative_stock_mask = df["stock_quantity"] < 0
    df.loc[negative_stock_mask, "stock_quantity"] = 0
    metrics["negative_stock_fixed"] = int(negative_stock_mask.sum())

    invalid_price_mask = df["selling_price"] < df["cost_price"]
    df.loc[invalid_price_mask, ["selling_price", "cost_price"]] = df.loc[invalid_price_mask, ["cost_price", "selling_price"]].to_numpy()
    metrics["price_validation_fixes"] = int(invalid_price_mask.sum())

    df["profit_margin"] = 0.0
    non_zero_cost = df["cost_price"] != 0
    df.loc[non_zero_cost, "profit_margin"] = ((df.loc[non_zero_cost, "selling_price"] - df.loc[non_zero_cost, "cost_price"]) / df.loc[non_zero_cost, "cost_price"]) * 100
    df["profit_margin"] = df["profit_margin"].round(2)

    LOGGER.info("Removed %s duplicate products", metrics["duplicate_products_removed"])
    LOGGER.info("Fixed %s negative stock values", metrics["negative_stock_fixed"])
    LOGGER.info("Adjusted %s invalid selling/cost price pairs", metrics["price_validation_fixes"])

    return df, metrics


def clean_orders(orders_df: pd.DataFrame, customers_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Standardize order dates, stabilize customer IDs, and flag customer existence."""
    df = orders_df.copy()
    metrics: dict[str, int] = {}

    df.columns = [str(column).strip() for column in df.columns]
    df["customer_id"] = df["customer_id"].apply(lambda value: pd.NA if pd.isna(value) or str(value).strip() == "" else str(value).strip())
    df["status"] = df["status"].fillna("UNKNOWN").astype(str).str.strip().str.upper()
    df["region_code"] = df["region_code"].fillna("UNKNOWN").astype(str).str.strip().str.upper()
    df["payment_method"] = df["payment_method"].fillna("UNKNOWN").astype(str).str.strip()

    original_dates = df["order_date"].copy()
    normalized_dates = []
    wrong_dates = 0
    future_dates = 0

    for value in original_dates:
        parsed = parse_datetime(value)
        if pd.isna(parsed):
            normalized_dates.append(pd.NaT)
            wrong_dates += 1
            continue

        if parsed > pd.Timestamp.now():
            parsed = pd.Timestamp.now()
            future_dates += 1

        normalized_dates.append(parsed)

    df["order_date"] = pd.to_datetime(normalized_dates, errors="coerce")
    df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    metrics["wrong_date_formats_fixed"] = wrong_dates
    metrics["future_dates_corrected"] = future_dates
    metrics["null_customer_ids_preserved"] = int(df["customer_id"].isna().sum())

    customer_ids = set(customers_df["customer_id"].dropna().astype(str))
    df["customer_exists"] = df["customer_id"].apply(lambda value: bool(value in customer_ids) if pd.notna(value) else False)

    LOGGER.info("Corrected %s wrong date formats", metrics["wrong_date_formats_fixed"])
    LOGGER.info("Fixed %s future dates", metrics["future_dates_corrected"])
    LOGGER.info("Kept %s NULL customer IDs as NaN", metrics["null_customer_ids_preserved"])

    return df, metrics


def clean_order_items(order_items_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Fix negative quantities, zero quantities, discounts, and price anomalies."""
    df = order_items_df.copy()
    metrics: dict[str, int] = {}

    df.columns = [str(column).strip() for column in df.columns]
    df["order_id"] = df["order_id"].apply(lambda value: pd.NA if pd.isna(value) or str(value).strip() == "" else str(value).strip())
    df["product_id"] = df["product_id"].apply(lambda value: pd.NA if pd.isna(value) or str(value).strip() == "" else str(value).strip())

    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1)
    negative_quantity_mask = df["quantity"] < 0
    df.loc[negative_quantity_mask, "quantity"] = df.loc[negative_quantity_mask, "quantity"].abs()
    metrics["negative_quantities_fixed"] = int(negative_quantity_mask.sum())

    zero_quantity_mask = df["quantity"] == 0
    df.loc[zero_quantity_mask, "quantity"] = 1

    df["discount_percent"] = pd.to_numeric(df["discount_percent"], errors="coerce").fillna(0)
    discount_low_mask = df["discount_percent"] < 0
    discount_high_mask = df["discount_percent"] > 100
    df.loc[discount_low_mask, "discount_percent"] = 0
    df.loc[discount_high_mask, "discount_percent"] = 100
    metrics["discount_errors_fixed"] = int((discount_low_mask | discount_high_mask).sum())

    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0)
    negative_price_mask = df["unit_price"] < 0
    df.loc[negative_price_mask, "unit_price"] = df.loc[negative_price_mask, "unit_price"].abs()

    LOGGER.info("Converted %s negative quantities to absolute values", metrics["negative_quantities_fixed"])
    LOGGER.info("Capped %s discount values to the lawful range", metrics["discount_errors_fixed"])

    return df, metrics


def check_referential_integrity(
    customers_df: pd.DataFrame,
    orders_df: pd.DataFrame,
    products_df: pd.DataFrame,
    order_items_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    """Check and flag broken customer, order, and product references without deleting rows."""
    customers_ids = set(customers_df["customer_id"].dropna().astype(str))
    orders_ids = set(orders_df["order_id"].dropna().astype(str))
    products_ids = set(products_df["product_id"].dropna().astype(str))

    orders_df = orders_df.copy()
    order_items_df = order_items_df.copy()

    orders_df["valid_customer"] = orders_df["customer_id"].apply(
        lambda value: bool(str(value) in customers_ids) if pd.notna(value) and str(value).strip() != "" else False
    )
    order_items_df["valid_order"] = order_items_df["order_id"].apply(
        lambda value: bool(str(value) in orders_ids) if pd.notna(value) and str(value).strip() != "" else False
    )
    order_items_df["valid_product"] = order_items_df["product_id"].apply(
        lambda value: bool(str(value) in products_ids) if pd.notna(value) and str(value).strip() != "" else False
    )

    missing_customers_df = orders_df.loc[~orders_df["valid_customer"], ["order_id", "customer_id"]].copy()
    missing_orders_df = order_items_df.loc[~order_items_df["valid_order"], ["item_id", "order_id"]].copy()
    missing_products_df = order_items_df.loc[~order_items_df["valid_product"], ["item_id", "product_id"]].copy()

    missing_customers_df.to_csv(OUTPUT_DIR / "missing_customers.csv", index=False)
    missing_orders_df.to_csv(OUTPUT_DIR / "missing_orders.csv", index=False)
    missing_products_df.to_csv(OUTPUT_DIR / "missing_products.csv", index=False)

    issue_count = len(missing_customers_df) + len(missing_orders_df) + len(missing_products_df)

    LOGGER.warning("Found %s referential integrity issues", issue_count)
    LOGGER.warning("Saved missing_customers.csv, missing_orders.csv, missing_products.csv")

    integrity_report = {
        "missing_customers": missing_customers_df,
        "missing_orders": missing_orders_df,
        "missing_products": missing_products_df,
        "referential_integrity_issues": int(issue_count),
        "missing_product_ids": int(len(missing_products_df)),
        "missing_order_ids": int(len(missing_orders_df)),
    }

    return orders_df, order_items_df, products_df, integrity_report


def run_cleaning_pipeline() -> dict[str, object]:
    """Execute the full cleaning workflow and export cleaned CSV files and reports."""
    datasets = load_raw_datasets()

    customers_df = datasets["customers"]
    products_df = datasets["products"]
    orders_df = datasets["orders"]
    order_items_df = datasets["order_items"]

    customers_clean, customer_metrics = clean_customers(customers_df)
    products_clean, product_metrics = clean_products(products_df)
    orders_clean, order_metrics = clean_orders(orders_df, customers_clean)
    order_items_clean, item_metrics = clean_order_items(order_items_df)

    orders_clean, order_items_clean, _, integrity_report = check_referential_integrity(
        customers_clean,
        orders_clean,
        products_clean,
        order_items_clean,
    )

    invalid_email_report = customer_metrics["invalid_emails_report"]
    invalid_email_path = save_invalid_email_report(invalid_email_report)

    customers_path = CLEANED_DATA_DIR / "customers_clean.csv"
    products_path = CLEANED_DATA_DIR / "products_clean.csv"
    orders_path = CLEANED_DATA_DIR / "orders_clean.csv"
    order_items_path = CLEANED_DATA_DIR / "order_items_clean.csv"

    customers_clean.to_csv(customers_path, index=False)
    products_clean.to_csv(products_path, index=False)
    orders_clean.to_csv(orders_path, index=False)
    order_items_clean.to_csv(order_items_path, index=False)

    LOGGER.info("Saved cleaned datasets to %s", CLEANED_DATA_DIR)

    report = {
        "customers_loaded": len(customers_df),
        "customers_cleaned": len(customers_clean),
        "duplicate_customers_removed": customer_metrics["duplicate_customers_removed"],
        "invalid_emails_corrected": customer_metrics["invalid_emails_corrected"],
        "missing_phone_fixed": customer_metrics["missing_phone_fixed"],
        "products_loaded": len(products_df),
        "products_cleaned": len(products_clean),
        "duplicate_products_removed": product_metrics["duplicate_products_removed"],
        "negative_stock_fixed": product_metrics["negative_stock_fixed"],
        "price_validation_fixes": product_metrics["price_validation_fixes"],
        "orders_loaded": len(orders_df),
        "orders_cleaned": len(orders_clean),
        "wrong_date_formats_fixed": order_metrics["wrong_date_formats_fixed"],
        "future_dates_corrected": order_metrics["future_dates_corrected"],
        "null_customer_ids_preserved": order_metrics["null_customer_ids_preserved"],
        "order_items_loaded": len(order_items_df),
        "order_items_cleaned": len(order_items_clean),
        "negative_quantities_fixed": item_metrics["negative_quantities_fixed"],
        "discount_errors_fixed": item_metrics["discount_errors_fixed"],
        "missing_product_ids": integrity_report["missing_product_ids"],
        "missing_order_ids": integrity_report["missing_order_ids"],
        "referential_integrity_issues": integrity_report["referential_integrity_issues"],
    }

    summary_df = create_summary_dataframe(report)
    summary_path = OUTPUT_DIR / "cleaning_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    report_path = OUTPUT_DIR / "cleaning_report.txt"
    generate_cleaning_report(report, report_path)

    print_terminal_summary(report)

    LOGGER.info("Summary saved to %s", summary_path)
    LOGGER.info("Invalid email report saved to %s", invalid_email_path)

    return report


if __name__ == "__main__":
    run_cleaning_pipeline()
