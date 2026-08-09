"""Run advanced SQL analytics and export every named result."""

from __future__ import annotations

import logging
import sqlite3
import time
from pathlib import Path

from scripts.database_utils import DATABASE_PATH, SQL_DIR, get_connection
from scripts.query_utils import execute_report, export_report, log_report_result, parse_report_queries

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output" / "advanced_reports"
SQL_FILES = {
    "window": "window_functions.sql",
    "cte": "cte_queries.sql",
    "cohort": "cohort_analysis.sql",
    "segmentation": "customer_segmentation.sql",
}


def configure_logging() -> None:
    """Configure persistent logging for the advanced analytics run."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(OUTPUT_DIR / "advanced_execution.log", encoding="utf-8"), logging.StreamHandler()],
        force=True,
    )


def run_advanced_reports() -> tuple[dict[str, int], float]:
    """Execute all advanced SQL reports and export CSV and TXT artifacts."""
    configure_logging()
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database does not exist: {DATABASE_PATH}")

    started = time.perf_counter()
    counts: dict[str, int] = {name: 0 for name in SQL_FILES}
    with get_connection(DATABASE_PATH) as connection:
        for group, file_name in SQL_FILES.items():
            sql_path = SQL_DIR / file_name
            if not sql_path.exists():
                raise FileNotFoundError(f"Required SQL file is missing: {sql_path}")
            for report_name, query in parse_report_queries(sql_path):
                report = execute_report(connection, report_name, query)
                export_report(report, report_name, OUTPUT_DIR)
                log_report_result(report_name, report)
                counts[group] += 1
    return counts, time.perf_counter() - started


def print_summary(counts: dict[str, int], elapsed: float) -> None:
    """Print the requested execution summary."""
    print("\nADVANCED ANALYTICS COMPLETED")
    print(f"Window Function Queries : {counts['window']}")
    print(f"CTE Queries : {counts['cte']}")
    print(f"Cohort Reports : {counts['cohort']}")
    print(f"Segmentation Reports : {counts['segmentation']}")
    print(f"Execution Time : {elapsed:.2f} sec")
    print("Execution Successful")


if __name__ == "__main__":
    try:
        print_summary(*run_advanced_reports())
    except (FileNotFoundError, RuntimeError, sqlite3.DatabaseError) as exc:
        logging.exception("Advanced analytics failed")
        raise SystemExit(f"Advanced analytics failed: {exc}") from exc
