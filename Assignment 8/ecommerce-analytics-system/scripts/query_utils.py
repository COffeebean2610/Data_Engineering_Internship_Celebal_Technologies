"""Helpers for discovering, executing, displaying, and exporting named SQL reports."""

from __future__ import annotations

import logging
import re
import sqlite3
from pathlib import Path

import pandas as pd

from scripts.table_formatter import format_table

LOGGER = logging.getLogger("ecommerce_analytics.sql")
REPORT_MARKER = re.compile(r"^\s*--\s*report:\s*([a-z0-9_]+)\s*$", re.IGNORECASE)


def parse_report_queries(sql_path: Path) -> list[tuple[str, str]]:
    """Parse report blocks marked with ``-- report: report_name`` from an SQL file."""
    reports: list[tuple[str, str]] = []
    current_name: str | None = None
    current_lines: list[str] = []
    for line in sql_path.read_text(encoding="utf-8").splitlines():
        match = REPORT_MARKER.match(line)
        if match:
            if current_name and current_lines:
                reports.append((current_name, "\n".join(current_lines).strip()))
            current_name, current_lines = match.group(1), []
        elif current_name:
            current_lines.append(line)
    if current_name and current_lines:
        reports.append((current_name, "\n".join(current_lines).strip()))
    if not reports:
        raise ValueError(f"No '-- report:' blocks found in {sql_path.name}")
    return reports


def execute_report(connection: sqlite3.Connection, name: str, query: str) -> pd.DataFrame:
    """Execute one SELECT report and return its result as a DataFrame."""
    try:
        return pd.read_sql_query(query, connection)
    except (sqlite3.DatabaseError, pd.errors.DatabaseError) as exc:
        raise RuntimeError(f"Report '{name}' failed: {exc}") from exc


def export_report(frame: pd.DataFrame, report_name: str, output_dir: Path) -> None:
    """Write a report to CSV and readable tabulated TXT, including empty reports."""
    output_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_dir / f"{report_name}.csv", index=False)
    rendered = format_table(frame, headers="keys", tablefmt="grid", showindex=False)
    (output_dir / f"{report_name}.txt").write_text(rendered + "\n", encoding="utf-8")


def log_report_result(report_name: str, frame: pd.DataFrame) -> None:
    """Log and print a compact preview suitable for an interactive terminal."""
    LOGGER.info("Executed %-42s rows=%s", report_name, len(frame))
    preview = frame.head(10)
    print(f"\n--- {report_name} ({len(frame)} rows) ---")
    print(format_table(preview, headers="keys", tablefmt="github", showindex=False))
