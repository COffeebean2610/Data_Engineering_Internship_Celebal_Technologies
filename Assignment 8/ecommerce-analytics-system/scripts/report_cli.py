"""Command-line entry point for dynamic E-Commerce SQLite reports."""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import date
from pathlib import Path

from scripts.database_manager import DatabaseUnavailableError, database_connection
from scripts.report_service import DateRange, available_reports, generate_report
from scripts.table_formatter import format_table

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output" / "reports"


def parse_iso_date(value: str) -> str:
    """Validate a YYYY-MM-DD argument and return its normalized value."""
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid date '{value}'. Use YYYY-MM-DD.") from exc


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser and usage documentation."""
    parser = argparse.ArgumentParser(description="Generate E-Commerce SQLite analytics reports.")
    parser.add_argument("--report", required=True, choices=available_reports(), help="Report to generate.")
    parser.add_argument("--start-date", type=parse_iso_date, help="Inclusive start date, YYYY-MM-DD.")
    parser.add_argument("--end-date", type=parse_iso_date, help="Inclusive end date, YYYY-MM-DD.")
    return parser


def export_report(report_name: str, data: object) -> tuple[Path, Path]:
    """Export a DataFrame as CSV and a readable terminal-style text report."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT_DIR / f"{report_name}_report.csv"
    text_path = OUTPUT_DIR / f"{report_name}_report.txt"
    data.to_csv(csv_path, index=False)
    text_path.write_text(format_table(data, headers="keys", tablefmt="grid", showindex=False) + "\n", encoding="utf-8")
    return csv_path, text_path


def format_currency(value: object) -> str:
    """Format numeric output as INR for portable terminal output."""
    try:
        return f"INR {float(value):,.2f}"
    except (TypeError, ValueError):
        return "N/A"


def print_report(title: str, data: object, date_range: DateRange, highlights: dict[str, object], elapsed: float) -> None:
    """Print a compact report header followed by a tabulated result preview."""
    range_label = f"{date_range.start_date or 'All data'} to {date_range.end_date or 'All data'}"
    print("\n==========================================")
    print("E-COMMERCE ANALYTICS REPORT")
    print("==========================================")
    print(f"Report: {title}")
    print(f"Date Range: {range_label}")
    if "total_revenue" in highlights:
        print(f"Total Revenue: {format_currency(highlights['total_revenue'])}")
        print(f"Total Orders: {highlights['total_orders']}")
        print(f"Average Order Value: {format_currency(highlights['average_order_value'])}")
        print(f"Top Customer: {highlights['top_customer']}")
        print(f"Top Product: {highlights['top_product']}")
    elif "rows" in highlights:
        print(f"Rows Returned: {highlights['rows']}")
    print()
    if data.empty:
        print("No data matched the selected report and date range.")
    else:
        print(format_table(data.head(25), headers="keys", tablefmt="github", showindex=False))
        if len(data) > 25:
            print(f"\nShowing 25 of {len(data)} rows; full output was exported.")
    print(f"\nReport saved to: {OUTPUT_DIR}")
    print(f"Execution Time: {elapsed:.2f} sec")
    print("==========================================")


def main() -> int:
    """Validate arguments, generate a report, export it, and return an exit code."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    arguments = build_parser().parse_args()
    if arguments.start_date and arguments.end_date and arguments.start_date > arguments.end_date:
        print("Error: --start-date must be on or before --end-date.", file=sys.stderr)
        return 2
    date_range = DateRange(arguments.start_date, arguments.end_date)
    started = time.perf_counter()
    try:
        with database_connection() as connection:
            result = generate_report(connection, arguments.report, date_range)
        export_report(arguments.report, result.data)
        print_report(result.title, result.data, date_range, result.highlights, time.perf_counter() - started)
        return 0
    except (DatabaseUnavailableError, RuntimeError, OSError) as exc:
        logging.error("Report generation failed: %s", exc)
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
