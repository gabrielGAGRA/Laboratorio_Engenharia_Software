"""Data transfer objects for tracks."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from app.domain.models.track import Track


@dataclass(slots=True, frozen=True, kw_only=True)
class TrackResponse:
    track_id: int | None
    title: str
    artist: str
    duration_seconds: int
    genre: str
    spotify_id: str | None = None
    album: str | None = None
    country: str | None = None
    release_year: int | None = None
    cover_url: str | None = None
    itunes_preview_url: str | None = None
    explicit: bool = False
    is_deleted: bool = False
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, track: Track) -> TrackResponse:
        return cls(
            track_id=track.track_id,
            title=track.title,
            artist=track.artist,
            duration_seconds=track.duration_seconds,
            genre=track.genre,
            spotify_id=track.spotify_id,
            album=track.album,
            country=track.country,
            release_year=track.release_year,
            cover_url=track.cover_url,
            itunes_preview_url=track.itunes_preview_url,
            explicit=track.explicit,
            is_deleted=track.is_deleted,
            created_at=track.created_at,
        )
