"""Execute the SQL analytics module and export every named business report."""

from __future__ import annotations

import logging
import sqlite3
import time
from pathlib import Path

from scripts.database_utils import DATABASE_PATH, SQL_DIR, get_connection
from scripts.query_utils import execute_report, export_report, log_report_result, parse_report_queries

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_ROOT / "output" / "sql_reports"
QUERY_FILES = ("basic_queries.sql", "join_queries.sql", "aggregation_queries.sql", "business_reports.sql")
VIEWS_FILE = SQL_DIR / "views.sql"


def configure_logging() -> None:
    """Configure file and terminal logging for repeatable SQL executions."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(REPORT_DIR / "sql_execution.log", encoding="utf-8"), logging.StreamHandler()],
        force=True,
    )


def create_views(connection: sqlite3.Connection) -> int:
    """Create or replace the six reusable analytics views."""
    if not VIEWS_FILE.exists():
        raise FileNotFoundError(f"Required SQL file is missing: {VIEWS_FILE}")
    connection.executescript(VIEWS_FILE.read_text(encoding="utf-8"))
    return connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE type = 'view'").fetchone()[0]


def run_analytics() -> tuple[int, int, int, float]:
    """Run all named report queries, export results, and return summary metrics."""
    configure_logging()
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database does not exist: {DATABASE_PATH}. Run main.py first.")

    started = time.perf_counter()
    query_count = report_count = 0
    with get_connection(DATABASE_PATH) as connection:
        view_count = create_views(connection)
        for file_name in QUERY_FILES:
            sql_path = SQL_DIR / file_name
            if not sql_path.exists():
                raise FileNotFoundError(f"Required SQL file is missing: {sql_path}")
            for report_name, query in parse_report_queries(sql_path):
                report = execute_report(connection, report_name, query)
                export_report(report, report_name, REPORT_DIR)
                log_report_result(report_name, report)
                query_count += 1
                report_count += 1
        # Export the public views as well, making their stable interfaces easy to consume.
        for view_name in ("customer_summary", "product_summary", "order_summary", "revenue_summary", "monthly_sales", "customer_revenue"):
            report = execute_report(connection, view_name, f"SELECT * FROM {view_name}")
            export_report(report, view_name, REPORT_DIR)
            log_report_result(view_name, report)
            report_count += 1
    elapsed = time.perf_counter() - started
    return query_count, report_count, view_count, elapsed


def print_summary(query_count: int, report_count: int, view_count: int, elapsed: float) -> None:
    """Print the final professional SQL analytics completion message."""
    print("\n==========================================")
    print("SQL ANALYTICS SUMMARY")
    print("==========================================")
    print(f"Queries Executed : {query_count}")
    print(f"Reports Generated : {report_count}")
    print(f"Views Created : {view_count}")
    print(f"Execution Time : {elapsed:.2f} sec")
    print("Output Folder : output/sql_reports/")
    print("Analytics Completed Successfully")
    print("==========================================")


if __name__ == "__main__":
    try:
        print_summary(*run_analytics())
    except (FileNotFoundError, RuntimeError, sqlite3.DatabaseError) as exc:
        logging.exception("SQL analytics failed")
        raise SystemExit(f"SQL analytics failed: {exc}") from exc
