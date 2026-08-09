"""Create the SQLite database and apply the versioned schema SQL files."""

from __future__ import annotations

from scripts.database_utils import DATABASE_PATH, SQL_DIR, execute_sql_file, get_connection


def create_database() -> None:
    """Recreate all tables safely, then apply constraints and performance indexes."""
    with get_connection(DATABASE_PATH) as connection:
        connection.executescript(
            "DROP TABLE IF EXISTS order_items; DROP TABLE IF EXISTS orders; "
            "DROP TABLE IF EXISTS products; DROP TABLE IF EXISTS customers;"
        )
        execute_sql_file(connection, SQL_DIR / "schema.sql")
        execute_sql_file(connection, SQL_DIR / "constraints.sql")
        execute_sql_file(connection, SQL_DIR / "indexes.sql")


if __name__ == "__main__":
    create_database()
