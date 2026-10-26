"""Jam repository implementation conforming to JamRepositoryPort."""

from app.infrastructure.adapters.sqlite.repositories.jam_repository import (
    SQLiteJamRepository,
)

JamRepository = SQLiteJamRepository

__all__ = ["JamRepository", "SQLiteJamRepository"]
