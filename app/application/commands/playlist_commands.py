"""Inbound application commands for playlist operations."""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateDeckPlaylistCommand:
    user_id: int
    name: str
    duration_minutes: int | None = None
    genre: str | None = None
    year: int | None = None
    artist: str | None = None
    country: str | None = None
    description: str | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class AddTrackToPlaylistCommand:
    playlist_id: int
    track_id: int
    user_id: int
