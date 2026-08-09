"""SQL-backed business report definitions for the reporting CLI."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class DateRange:
    """Inclusive ISO date range passed to data-bearing reports."""

    start_date: str | None = None
    end_date: str | None = None


@dataclass
class ReportResult:
    """Result data and terminal-friendly metadata for a requested report."""

    title: str
    data: pd.DataFrame
    highlights: dict[str, Any]


REPORT_TITLES = {
    "revenue": "Revenue Summary",
    "orders": "Order Summary",
    "customers": "Customer Summary",
    "products": "Product Summary",
    "monthly_sales": "Monthly Sales",
    "category": "Category Revenue",
    "region": "Region Revenue",
    "top_customers": "Top Customers",
    "top_products": "Top Products",
    "segmentation": "Customer Segmentation",
    "cohort": "Cohort Analysis",
    "retention": "Retention Report",
    "returns": "Return Analysis",
}


def available_reports() -> tuple[str, ...]:
    """Return valid command-line report names."""
    return tuple(REPORT_TITLES)


def _date_filter(date_range: DateRange, alias: str = "o") -> tuple[str, list[str]]:
    clauses: list[str] = []
    parameters: list[str] = []
    if date_range.start_date:
        clauses.append(f"date({alias}.order_date) >= date(?)")
        parameters.append(date_range.start_date)
    if date_range.end_date:
        clauses.append(f"date({alias}.order_date) <= date(?)")
        parameters.append(date_range.end_date)
    return (" AND " + " AND ".join(clauses) if clauses else ""), parameters


def _read_sql(connection: sqlite3.Connection, query: str, parameters: list[str]) -> pd.DataFrame:
    """Run one parameterized query and normalize SQLite failures."""
    try:
        return pd.read_sql_query(query, connection, params=parameters)
    except (sqlite3.Error, pd.errors.DatabaseError) as exc:
        raise RuntimeError(f"Report query failed: {exc}") from exc


def _revenue_summary(connection: sqlite3.Connection, date_range: DateRange) -> ReportResult:
    filter_sql, params = _date_filter(date_range)
    query = f"""
        SELECT ROUND(COALESCE(SUM(i.quantity * i.unit_price *
               (1 - i.discount_percent / 100.0)), 0), 2) AS total_revenue,
               COUNT(DISTINCT o.order_id) AS total_orders,
               ROUND(COALESCE(SUM(i.quantity * i.unit_price *
               (1 - i.discount_percent / 100.0)) / NULLIF(COUNT(DISTINCT o.order_id), 0), 0), 2) AS average_order_value
        FROM orders o LEFT JOIN order_items i ON i.order_id = o.order_id
        WHERE 1 = 1 {filter_sql}
    """
    data = _read_sql(connection, query, params)
    top_customer = _read_sql(connection, f"""
        SELECT c.customer_name FROM customers c JOIN orders o ON o.customer_id = c.customer_id
        JOIN order_items i ON i.order_id = o.order_id WHERE 1 = 1 {filter_sql}
        GROUP BY c.customer_id, c.customer_name ORDER BY SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) DESC LIMIT 1
    """, params)
    top_product = _read_sql(connection, f"""
        SELECT p.product_name FROM products p JOIN order_items i ON i.product_id = p.product_id
        JOIN orders o ON o.order_id = i.order_id WHERE 1 = 1 {filter_sql}
        GROUP BY p.product_id, p.product_name ORDER BY SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) DESC LIMIT 1
    """, params)
    row = data.iloc[0].to_dict()
    row["top_customer"] = top_customer.iloc[0, 0] if not top_customer.empty else "N/A"
    row["top_product"] = top_product.iloc[0, 0] if not top_product.empty else "N/A"
    return ReportResult(REPORT_TITLES["revenue"], data, row)


def _aggregate_report(connection: sqlite3.Connection, report_name: str, date_range: DateRange) -> ReportResult:
    filter_sql, params = _date_filter(date_range)
    definitions = {
        "orders": ("""SELECT o.status, COUNT(*) AS orders, ROUND(COALESCE(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 0), 2) AS revenue FROM orders o LEFT JOIN order_items i ON i.order_id = o.order_id WHERE 1 = 1 {filter} GROUP BY o.status ORDER BY orders DESC""", {}),
        "customers": ("""SELECT c.customer_id, c.customer_name, c.customer_type, COUNT(DISTINCT o.order_id) AS orders, ROUND(COALESCE(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 0), 2) AS revenue FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id {filter} LEFT JOIN order_items i ON i.order_id = o.order_id GROUP BY c.customer_id, c.customer_name, c.customer_type ORDER BY revenue DESC""", {}),
        "products": ("""SELECT p.product_id, p.product_name, p.category, COALESCE(SUM(i.quantity), 0) AS units_sold, ROUND(COALESCE(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 0), 2) AS revenue FROM products p LEFT JOIN order_items i ON i.product_id = p.product_id LEFT JOIN orders o ON o.order_id = i.order_id WHERE (o.order_id IS NULL OR 1 = 1 {filter}) GROUP BY p.product_id, p.product_name, p.category ORDER BY revenue DESC""", {}),
        "monthly_sales": ("""SELECT strftime('%Y-%m', o.order_date) AS sales_month, COUNT(DISTINCT o.order_id) AS orders, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id WHERE 1 = 1 {filter} GROUP BY sales_month ORDER BY sales_month""", {}),
        "category": ("""SELECT p.category, SUM(i.quantity) AS units_sold, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM products p JOIN order_items i ON i.product_id = p.product_id JOIN orders o ON o.order_id = i.order_id WHERE 1 = 1 {filter} GROUP BY p.category ORDER BY revenue DESC""", {}),
        "region": ("""SELECT o.region_code, COUNT(DISTINCT o.order_id) AS orders, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id WHERE 1 = 1 {filter} GROUP BY o.region_code ORDER BY revenue DESC""", {}),
        "top_customers": ("""SELECT c.customer_id, c.customer_name, COUNT(DISTINCT o.order_id) AS orders, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM customers c JOIN orders o ON o.customer_id = c.customer_id JOIN order_items i ON i.order_id = o.order_id WHERE 1 = 1 {filter} GROUP BY c.customer_id, c.customer_name ORDER BY revenue DESC LIMIT 20""", {}),
        "top_products": ("""SELECT p.product_id, p.product_name, p.category, SUM(i.quantity) AS units_sold, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM products p JOIN order_items i ON i.product_id = p.product_id JOIN orders o ON o.order_id = i.order_id WHERE 1 = 1 {filter} GROUP BY p.product_id, p.product_name, p.category ORDER BY revenue DESC LIMIT 20""", {}),
        "returns": ("""SELECT p.product_id, p.product_name, p.category, SUM(CASE WHEN o.status = 'RETURNED' THEN i.quantity ELSE 0 END) AS returned_units, ROUND(100.0 * SUM(CASE WHEN o.status = 'RETURNED' THEN i.quantity ELSE 0 END) / NULLIF(SUM(i.quantity), 0), 2) AS return_rate_percent FROM products p JOIN order_items i ON i.product_id = p.product_id JOIN orders o ON o.order_id = i.order_id WHERE 1 = 1 {filter} GROUP BY p.product_id, p.product_name, p.category ORDER BY returned_units DESC""", {}),
    }
    template, _ = definitions[report_name]
    query = template.format(filter=filter_sql)
    data = _read_sql(connection, query, params)
    return ReportResult(REPORT_TITLES[report_name], data, {"rows": len(data)})


def _advanced_report(connection: sqlite3.Connection, report_name: str, date_range: DateRange) -> ReportResult:
    filter_sql, params = _date_filter(date_range)
    if report_name == "segmentation":
        query = f"""WITH base AS (SELECT c.customer_id, c.customer_name, COUNT(DISTINCT o.order_id) AS frequency, COALESCE(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 0) AS monetary FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id AND 1 = 1 {filter_sql} LEFT JOIN order_items i ON i.order_id = o.order_id GROUP BY c.customer_id, c.customer_name) SELECT customer_id, customer_name, frequency, ROUND(monetary, 2) AS monetary, CASE WHEN frequency <= 1 THEN 'One-Time' WHEN frequency <= 4 THEN 'Occasional' ELSE 'Loyal' END AS frequency_segment, CASE WHEN monetary < 10000 THEN 'Low' WHEN monetary < 50000 THEN 'Medium' ELSE 'High' END AS spend_segment FROM base ORDER BY monetary DESC"""
    elif report_name == "cohort":
        query = f"""WITH customer_months AS (SELECT customer_id, date(strftime('%Y-%m-01', order_date)) AS purchase_month FROM orders o WHERE customer_id IS NOT NULL {filter_sql} GROUP BY customer_id, purchase_month), cohorts AS (SELECT customer_id, MIN(purchase_month) AS cohort_month FROM customer_months GROUP BY customer_id), activity AS (SELECT c.cohort_month, ((CAST(strftime('%Y', cm.purchase_month) AS INTEGER) - CAST(strftime('%Y', c.cohort_month) AS INTEGER)) * 12 + CAST(strftime('%m', cm.purchase_month) AS INTEGER) - CAST(strftime('%m', c.cohort_month) AS INTEGER)) AS month_number, cm.customer_id FROM customer_months cm JOIN cohorts c ON c.customer_id = cm.customer_id), sizes AS (SELECT cohort_month, COUNT(DISTINCT customer_id) AS customers FROM activity WHERE month_number = 0 GROUP BY cohort_month) SELECT a.cohort_month, a.month_number, COUNT(DISTINCT a.customer_id) AS active_customers, s.customers AS cohort_customers, ROUND(100.0 * COUNT(DISTINCT a.customer_id) / s.customers, 2) AS retention_percent FROM activity a JOIN sizes s ON s.cohort_month = a.cohort_month WHERE a.month_number BETWEEN 0 AND 3 GROUP BY a.cohort_month, a.month_number, s.customers ORDER BY a.cohort_month, a.month_number"""
    else:
        query = f"""WITH latest AS (SELECT c.customer_id, MAX(date(o.order_date)) AS latest_order_date FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id AND 1 = 1 {filter_sql} GROUP BY c.customer_id), status AS (SELECT CASE WHEN latest_order_date IS NULL OR latest_order_date < date('now', '-90 days') THEN 'Churned' ELSE 'Active' END AS retention_status FROM latest) SELECT retention_status, COUNT(*) AS customers, ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS customer_percent FROM status GROUP BY retention_status"""
    data = _read_sql(connection, query, params)
    return ReportResult(REPORT_TITLES[report_name], data, {"rows": len(data)})


def generate_report(connection: sqlite3.Connection, report_name: str, date_range: DateRange) -> ReportResult:
    """Generate a supported report using only parameterized date predicates."""
    if report_name not in REPORT_TITLES:
        raise ValueError(f"Unknown report '{report_name}'. Choose from: {', '.join(available_reports())}")
    if report_name == "revenue":
        return _revenue_summary(connection, date_range)
    if report_name in {"segmentation", "cohort", "retention"}:
        return _advanced_report(connection, report_name, date_range)
    return _aggregate_report(connection, report_name, date_range)
