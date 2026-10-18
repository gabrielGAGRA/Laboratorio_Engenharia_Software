"""Playlist repository implementation conforming to PlaylistRepositoryPort."""

from app.infrastructure.adapters.sqlite.repositories.playlist_repository import (
    SQLitePlaylistRepository,
)

PlaylistRepository = SQLitePlaylistRepository

__all__ = ["PlaylistRepository", "SQLitePlaylistRepository"]
