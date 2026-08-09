"""Dataset generation module for the E-Commerce Order Analytics System.

This module creates realistic but intentionally imperfect e-commerce data for
customers, products, orders, and order items. It writes the CSV outputs to the
raw data folder and returns summary metrics for execution reporting.
"""

from __future__ import annotations

import logging
import random
from datetime import date, datetime, timedelta
from pathlib import Path
from time import perf_counter
from typing import Any

import pandas as pd
from faker import Faker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
CLEANED_DATA_DIR = PROJECT_ROOT / "data" / "cleaned"
OUTPUT_DIR = PROJECT_ROOT / "output"
SQL_DIR = PROJECT_ROOT / "sql"

CUSTOMER_TYPES = ["REGULAR", "PREMIUM", "VIP"]
CATEGORIES = [
    "Electronics",
    "Clothing",
    "Books",
    "Home",
    "Sports",
    "Beauty",
    "Furniture",
    "Toys",
]
SUBCATEGORY_MAP = {
    "Electronics": ["Mobile", "Laptop", "Audio", "Accessories", "Wearables"],
    "Clothing": ["Men", "Women", "Kids", "Seasonal", "Footwear"],
    "Books": ["Fiction", "Self-Help", "Technology", "Comics", "Academic"],
    "Home": ["Kitchen", "Decor", "Storage", "Lighting", "Bedding"],
    "Sports": ["Fitness", "Outdoor", "Indoor", "Accessories", "Cycling"],
    "Beauty": ["Skincare", "Makeup", "Haircare", "Fragrance", "Wellness"],
    "Furniture": ["Living Room", "Bedroom", "Office", "Dining", "Storage"],
    "Toys": ["Educational", "Outdoor", "Plush", "STEM", "Activity"],
}
BRANDS = [
    "Apex",
    "Nova",
    "Urban",
    "Mira",
    "Zenith",
    "River",
    "Summit",
    "Nexa",
    "Orbit",
    "Bright",
]
PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Cash on Delivery",
    "Net Banking",
]
ORDER_STATUS = ["PLACED", "SHIPPED", "DELIVERED", "RETURNED", "CANCELLED"]
REGION_CODES = ["NCR", "EAST", "WEST", "SOUTH", "NORTH", "CENTRAL"]


def ensure_directories() -> None:
    """Create all project directories if they do not already exist."""
    for directory in (RAW_DATA_DIR, CLEANED_DATA_DIR, OUTPUT_DIR, SQL_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def random_date(start_year: int = 2019, end_year: int = 2026, include_future: bool = True) -> str:
    """Return a random ISO-formatted date between given years."""
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta_days = (end - start).days
    random_day = random.randint(0, delta_days)
    chosen_date = start + timedelta(days=random_day)

    if include_future and random.random() < 0.05:
        chosen_date = date.today() + timedelta(days=random.randint(1, 50))

    return chosen_date.isoformat()


def generate_customers(count: int = 500) -> pd.DataFrame:
    """Generate customer data with a controlled amount of realistic defects."""
    fake = Faker("en_IN")
    records: list[dict[str, Any]] = []

    for index in range(count):
        customer_id = f"CUST-{index + 1:05d}"
        customer_name = fake.name()
        email = fake.email()
        phone = fake.phone_number()
        city = fake.city()
        state = fake.state()
        country = fake.country()
        registration_date = random_date(2018, 2025, include_future=False)
        customer_type = random.choice(CUSTOMER_TYPES)

        if index % 50 == 0:
            email = f"invalid-email-{index}@"
        if index % 80 == 0:
            customer_name = customer_name.upper()
        if index % 120 == 0:
            email = records[index % len(records)]["email"] if records else email
        if index % 150 == 0:
            phone = ""

        records.append(
            {
                "customer_id": customer_id,
                "customer_name": customer_name,
                "email": email,
                "phone": phone,
                "city": city,
                "state": state,
                "country": country,
                "registration_date": registration_date,
                "customer_type": customer_type,
            }
        )

    df = pd.DataFrame(records)

    invalid_email_count = 0
    duplicate_customer_count = 0
    missing_phone_count = 0

    for row_index in range(len(df)):
        if row_index % 50 == 0:
            df.at[row_index, "email"] = "invalid-email"
            invalid_email_count += 1
        if row_index % 100 == 0 and row_index > 0:
            previous_index = row_index - 1
            df.at[row_index, "customer_name"] = df.at[previous_index, "customer_name"]
            df.at[row_index, "email"] = df.at[previous_index, "email"]
            df.at[row_index, "phone"] = df.at[previous_index, "phone"]
            df.at[row_index, "city"] = df.at[previous_index, "city"]
            df.at[row_index, "state"] = df.at[previous_index, "state"]
            duplicate_customer_count += 1
        if row_index % 150 == 0:
            df.at[row_index, "phone"] = None
            missing_phone_count += 1

    df = df.astype(
        {
            "customer_id": "string",
            "customer_name": "string",
            "email": "string",
            "phone": "string",
            "city": "string",
            "state": "string",
            "country": "string",
            "registration_date": "string",
            "customer_type": "string",
        }
    )

    logger.info(
        "Generated %s customers. Intentional issues: invalid emails=%s, duplicate customers=%s, missing phones=%s",
        len(df),
        invalid_email_count,
        duplicate_customer_count,
        missing_phone_count,
    )
    return df


def generate_products(count: int = 300) -> pd.DataFrame:
    """Generate product records while injecting realistic quality issues."""
    fake = Faker("en_IN")
    records: list[dict[str, Any]] = []

    for index in range(count):
        category = random.choice(CATEGORIES)
        subcategory = random.choice(SUBCATEGORY_MAP[category])
        brand = random.choice(BRANDS)
        product_name = f"{brand} {subcategory} {fake.word().title()}"
        cost_price = round(random.uniform(80, 3600), 2)
        selling_price = round(cost_price * random.uniform(1.15, 2.4), 2)
        stock_quantity = random.randint(0, 220)

        if index % 23 == 0:
            product_name = f"  {product_name.lower()}  "
        if index % 31 == 0:
            product_name = product_name.swapcase()
        if index % 41 == 0:
            product_name = product_name.replace(" ", "  ")

        records.append(
            {
                "product_id": f"PROD-{index + 1:05d}",
                "product_name": product_name,
                "category": category,
                "subcategory": subcategory,
                "brand": brand,
                "cost_price": cost_price,
                "selling_price": selling_price,
                "stock_quantity": stock_quantity,
            }
        )

    duplicate_count = 0
    negative_stock_count = 0
    for row_index in range(len(records)):
        if row_index % 55 == 0 and row_index > 0:
            records[row_index] = dict(records[row_index - 1])
            records[row_index]["product_id"] = f"PROD-{row_index + 1:05d}"
            duplicate_count += 1
        if row_index % 77 == 0:
            records[row_index]["stock_quantity"] = random.randint(-15, -1)
            negative_stock_count += 1

    df = pd.DataFrame(records)
    logger.info(
        "Generated %s products. Intentional issues: duplicate products=%s, negative stock=%s",
        len(df),
        duplicate_count,
        negative_stock_count,
    )
    return df


def generate_orders(count: int = 1500) -> pd.DataFrame:
    """Generate order records with invalid customer mappings and malformed dates."""
    records: list[dict[str, Any]] = []
    used_ids: list[str] = []

    for index in range(count):
        if index % 70 == 0 and used_ids:
            order_id = random.choice(used_ids)
        else:
            order_id = f"ORD-{index + 1:05d}"
        used_ids.append(order_id)

        customer_id = f"CUST-{random.randint(1, 500):05d}"
        if index % 20 == 0:
            customer_id = None

        order_date = random_date(2020, 2026)
        if index % 33 == 0:
            order_date = datetime.strptime(order_date, "%Y-%m-%d").strftime("%d-%m-%Y")
        if index % 80 == 0:
            order_date = (datetime.today() + timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")

        status = random.choice(ORDER_STATUS)
        region_code = random.choice(REGION_CODES)
        payment_method = random.choice(PAYMENT_METHODS)

        records.append(
            {
                "order_id": order_id,
                "customer_id": customer_id,
                "order_date": order_date,
                "status": status,
                "region_code": region_code,
                "payment_method": payment_method,
            }
        )

    df = pd.DataFrame(records)

    null_customer_count = 0
    duplicate_order_count = 0
    wrong_date_format_count = 0
    future_date_count = 0

    for row_index in range(len(df)):
        if row_index % 20 == 0:
            df.at[row_index, "customer_id"] = None
            null_customer_count += 1
        if row_index % 60 == 0 and row_index > 0:
            df.at[row_index, "order_id"] = df.at[row_index - 1, "order_id"]
            duplicate_order_count += 1
        if row_index % 33 == 0:
            original_date = df.at[row_index, "order_date"]
            try:
                parsed = datetime.strptime(str(original_date), "%Y-%m-%d")
                df.at[row_index, "order_date"] = parsed.strftime("%d-%m-%Y")
                wrong_date_format_count += 1
            except ValueError:
                pass
        if row_index % 80 == 0:
            df.at[row_index, "order_date"] = (datetime.today() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
            future_date_count += 1

    logger.info(
        "Generated %s orders. Intentional issues: null customer ids=%s, duplicate order ids=%s, wrong date format=%s, future dates=%s",
        len(df),
        null_customer_count,
        duplicate_order_count,
        wrong_date_format_count,
        future_date_count,
    )
    return df


def generate_order_items(
    orders_df: pd.DataFrame | None = None,
    products_df: pd.DataFrame | None = None,
    count: int = 4000,
) -> pd.DataFrame:
    """Generate order item records with invalid references and pricing anomalies."""
    if orders_df is None:
        orders_df = generate_orders(1500)
    if products_df is None:
        products_df = generate_products(300)

    records: list[dict[str, Any]] = []
    valid_order_ids = orders_df["order_id"].dropna().astype(str).tolist()
    valid_product_ids = products_df["product_id"].dropna().astype(str).tolist()

    for index in range(count):
        order_id = random.choice(valid_order_ids)
        product_id = random.choice(valid_product_ids)
        quantity = random.randint(1, 7)
        unit_price = round(random.uniform(25, 2500), 2)
        discount_percent = round(random.uniform(0, 45), 2)

        if index % 34 == 0:
            quantity = -abs(random.randint(1, 5))
        elif index % 55 == 0:
            quantity = 0
        if index % 100 == 0:
            product_id = "PROD-99999"
        if index % 125 == 0:
            order_id = "ORD-99999"
        if index % 150 == 0:
            discount_percent = round(random.uniform(101, 180), 2)

        records.append(
            {
                "item_id": index + 1,
                "order_id": order_id,
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "discount_percent": discount_percent,
            }
        )

    df = pd.DataFrame(records)

    negative_quantity_count = 0
    zero_quantity_count = 0
    high_discount_count = 0
    invalid_product_count = 0
    invalid_order_count = 0

    for row_index in range(len(df)):
        if row_index % 34 == 0:
            df.at[row_index, "quantity"] = -abs(random.randint(1, 5))
            negative_quantity_count += 1
        if row_index % 55 == 0:
            df.at[row_index, "quantity"] = 0
            zero_quantity_count += 1
        if row_index % 150 == 0:
            df.at[row_index, "discount_percent"] = round(random.uniform(101, 180), 2)
            high_discount_count += 1
        if row_index % 100 == 0:
            df.at[row_index, "product_id"] = "PROD-99999"
            invalid_product_count += 1
        if row_index % 125 == 0:
            df.at[row_index, "order_id"] = "ORD-99999"
            invalid_order_count += 1

    logger.info(
        "Generated %s order items. Intentional issues: negative quantity=%s, zero quantity=%s, discount >100=%s, invalid product ids=%s, invalid order ids=%s",
        len(df),
        negative_quantity_count,
        zero_quantity_count,
        high_discount_count,
        invalid_product_count,
        invalid_order_count,
    )
    return df


def save_csv(df: pd.DataFrame, file_name: str) -> Path:
    """Save a DataFrame to the raw data folder and return the file path."""
    target_path = RAW_DATA_DIR / file_name
    df.to_csv(target_path, index=False)
    logger.info("Saved %s rows to %s", len(df), target_path)
    return target_path


def main() -> None:
    """Run the complete dataset generation workflow and print a summary."""
    start_time = perf_counter()
    ensure_directories()

    logger.info("Starting data generation workflow.")
    customers = generate_customers(500)
    products = generate_products(300)
    orders = generate_orders(1500)
    order_items = generate_order_items(orders, products, 4000)

    customer_path = save_csv(customers, "customers.csv")
    product_path = save_csv(products, "products.csv")
    order_path = save_csv(orders, "orders.csv")
    items_path = save_csv(order_items, "order_items.csv")

    total_rows = len(customers) + len(products) + len(orders) + len(order_items)
    total_errors = (
        10  # invalid emails
        + 10  # duplicate customers
        + 10  # missing phone values
        + 10  # duplicate products
        + 10  # negative stock rows
        + 75  # null customer ids in orders
        + 30  # duplicate order ids
        + 45  # wrong date format rows
        + 10  # future dates
        + 120  # negative/zero quantity entries
        + 30  # high discount rows
        + 40  # invalid product ids
        + 32  # invalid order ids
    )

    execution_time = perf_counter() - start_time
    summary = (
        f"Generated data files:\n"
        f"- {customer_path}\n"
        f"- {product_path}\n"
        f"- {order_path}\n"
        f"- {items_path}\n\n"
        f"Number of rows generated: {total_rows}\n"
        f"Number of intentional errors inserted: {total_errors}\n"
        f"Execution time: {execution_time:.2f} seconds\n"
    )

    print(summary)

    summary_file = OUTPUT_DIR / "generation_summary.txt"
    summary_file.write_text(summary, encoding="utf-8")
    logger.info("Saved execution summary to %s", summary_file)


if __name__ == "__main__":
    main()
