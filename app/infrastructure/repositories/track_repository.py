"""Track repository implementation conforming to TrackRepositoryPort."""

from app.infrastructure.adapters.sqlite.repositories.track_repository import (
    SQLiteTrackRepository,
)

TrackRepository = SQLiteTrackRepository

__all__ = ["SQLiteTrackRepository", "TrackRepository"]
