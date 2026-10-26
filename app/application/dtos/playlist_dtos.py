"""Data transfer objects for playlists."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.application.dtos.track_dtos import TrackResponse

if TYPE_CHECKING:
    from datetime import datetime

    from app.domain.models.playlist import Playlist


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateDeckPlaylistInput:
    user_id: int
    name: str
    duration_minutes: int | None = None
    genre: str | None = None
    year: int | None = None
    artist: str | None = None
    country: str | None = None
    description: str | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class AddTrackToPlaylistInput:
    playlist_id: int
    track_id: int
    user_id: int


@dataclass(slots=True, frozen=True, kw_only=True)
class PlaylistResponse:
    playlist_id: int | None
    user_id: int
    name: str
    description: str | None
    spotify_playlist_id: str | None
    is_exported: bool
    tracks: list[TrackResponse]
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, playlist: Playlist) -> PlaylistResponse:
        return cls(
            playlist_id=playlist.playlist_id,
            user_id=playlist.user_id,
            name=playlist.name,
            description=playlist.description,
            spotify_playlist_id=playlist.spotify_playlist_id,
            is_exported=playlist.is_exported,
            tracks=[TrackResponse.from_domain(t) for t in playlist.tracks],
            created_at=playlist.created_at,
        )
