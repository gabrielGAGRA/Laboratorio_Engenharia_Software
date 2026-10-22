"""Persistence ports used when feeding the database from Spotify."""

from typing import Protocol

from app.application.dtos.spotify_dtos import PlaylistImport, TrackImport


class TrackRepository(Protocol):
    def upsert_by_spotify_id(self, track: TrackImport) -> None: ...


class PlaylistRepository(Protocol):
    def save_imported(self, playlist: PlaylistImport) -> None: ...


__all__ = ["PlaylistRepository", "TrackRepository"]
