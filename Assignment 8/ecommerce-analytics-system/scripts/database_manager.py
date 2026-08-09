"""Safe SQLite connection management for command-line reports."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "ecommerce.db"


class DatabaseUnavailableError(RuntimeError):
    """Raised when the reporting database cannot be opened."""


@contextmanager
def database_connection(database_path: Path = DATABASE_PATH) -> Iterator[sqlite3.Connection]:
    """Open a read-only SQLite connection and close it reliably."""
    if not database_path.exists():
        raise DatabaseUnavailableError(
            f"Database not found at {database_path}. Run main.py before requesting reports."
        )
    try:
        connection = sqlite3.connect(f"file:{database_path.as_posix()}?mode=ro", uri=True)
        connection.execute("PRAGMA foreign_keys = ON")
        yield connection
    except sqlite3.Error as exc:
        raise DatabaseUnavailableError(f"Could not connect to the database: {exc}") from exc
    finally:
        if "connection" in locals():
            connection.close()
