"""Utility functions shared across the cleaning and validation pipeline."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
CLEANED_DATA_DIR = PROJECT_ROOT / "data" / "cleaned"
OUTPUT_DIR = PROJECT_ROOT / "output"


def setup_logging() -> logging.Logger:
    """Create and return a configured project logger."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True,
    )
    return logging.getLogger("ecommerce_analytics")


LOGGER = setup_logging()


def ensure_directories() -> None:
    """Ensure required project directories exist."""
    for directory in (RAW_DATA_DIR, CLEANED_DATA_DIR, OUTPUT_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace from column names and return a cleaned DataFrame."""
    df = df.copy()
    df.columns = [str(column).strip() for column in df.columns]
    return df


def clean_text(value: Any) -> str:
    """Normalize string values by stripping spaces and converting empty values."""
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return text if text else ""


def validate_email(email: Any) -> bool:
    """Validate whether a value resembles a valid email address."""
    if pd.isna(email):
        return False

    value = str(email).strip().lower()
    if not value or value in {"nan", "none", "null"}:
        return False

    if value.count("@") != 1:
        return False

    local_part, domain = value.split("@", 1)
    if not local_part or not domain:
        return False

    if "." not in domain:
        return False

    if any(char.isspace() for char in value):
        return False

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.fullmatch(pattern, value))


def parse_datetime(value: Any) -> pd.Timestamp | pd.NaT:
    """Parse a flexible date value into a pandas timestamp."""
    if pd.isna(value):
        return pd.NaT

    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return pd.NaT

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%m-%d-%Y",
        "%m/%d/%Y",
        "%d-%m-%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return pd.to_datetime(text, format=fmt)
        except (TypeError, ValueError):
            continue

    try:
        return pd.to_datetime(text, errors="raise")
    except (TypeError, ValueError):
        return pd.NaT


def normalize_category(value: Any) -> str:
    """Normalize category values to title case and keep them consistent."""
    text = clean_text(value)
    if not text:
        return ""
    return text.title()


def safe_numeric(value: Any, default: float = 0.0) -> float:
    """Convert a value to float while handling invalid inputs safely."""
    if pd.isna(value):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def load_csv_with_checks(file_path: Path, expected_columns: list[str] | None = None) -> pd.DataFrame:
    """Load a CSV with error handling for missing files and malformed data."""
    if not file_path.exists():
        raise FileNotFoundError(f"Missing required file: {file_path}")

    if file_path.stat().st_size == 0:
        raise ValueError(f"File is empty: {file_path}")

    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="latin-1")

    df = normalize_column_names(df)

    if expected_columns:
        missing_columns = [column for column in expected_columns if column not in df.columns]
        if missing_columns:
            raise ValueError(
                f"Incorrect columns in {file_path.name}. Missing: {', '.join(missing_columns)}"
            )

    return df
