"""On-demand database initialization utility and CLI command."""

import argparse
import logging
from pathlib import Path

from app.infrastructure.adapters.sqlite.connection import (
    DEFAULT_DATABASE_PATH,
    create_connection,
)

logger = logging.getLogger(__name__)
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def init_db(database_path: str = DEFAULT_DATABASE_PATH) -> None:
    """Executes the DDL schema against the specified SQLite database file."""
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with create_connection(database_path) as conn:
        conn.executescript(schema_sql)
        conn.commit()
    logger.info("Database initialized successfully at %s", database_path)


def main() -> None:
    """CLI entrypoint for initializing the local SQLite database."""
    parser = argparse.ArgumentParser(
        description="Initialize local Ribbit SQLite database schema."
    )
    parser.add_argument(
        "--db-path",
        default=DEFAULT_DATABASE_PATH,
        help="Target SQLite database file path.",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    init_db(args.db_path)
    logger.info("Database schema created at %s", args.db_path)


if __name__ == "__main__":
    main()


__all__ = ["init_db", "main"]
