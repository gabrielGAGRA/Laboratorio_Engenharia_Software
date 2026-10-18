"""Playlist and track presentation schemas."""

from pydantic import BaseModel, ConfigDict, Field


class TrackResponse(BaseModel):
    """Public representation of a catalog track."""

    model_config = ConfigDict(from_attributes=True)

    track_id: int
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


class DeckPlaylistRequest(BaseModel):
    """Payload for generating a dynamic deck playlist."""

    user_id: int
    name: str = Field(min_length=1, max_length=100)
    duration_minutes: int | None = Field(default=None, ge=1, le=600)
    genre: str | None = None
    year: int | None = Field(default=None, ge=1900, le=2100)
    artist: str | None = None
    country: str | None = None
    description: str | None = Field(default=None, max_length=500)


class SwipeAddTrackRequest(BaseModel):
    """Payload for adding a swiped track to a playlist."""

    track_id: int


class PlaylistResponse(BaseModel):
    """Public representation of a playlist and its tracks."""

    model_config = ConfigDict(from_attributes=True)

    playlist_id: int
    user_id: int
    name: str
    description: str | None = None
    spotify_playlist_id: str | None = None
    is_exported: bool = False
    tracks: list[TrackResponse] = Field(default_factory=list)


__all__ = [
    "DeckPlaylistRequest",
    "PlaylistResponse",
    "SwipeAddTrackRequest",
    "TrackResponse",
]
