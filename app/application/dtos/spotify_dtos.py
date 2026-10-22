"""Spotify boundary DTOs shared by ports, adapters and use cases."""

from pydantic import BaseModel, ConfigDict


class _FrozenDto(BaseModel):
    model_config = ConfigDict(frozen=True)


class SpotifyTokens(_FrozenDto):
    access_token: str
    expires_in: int
    refresh_token: str | None = None
    scope: str | None = None


class SpotifyTrack(_FrozenDto):
    spotify_id: str
    uri: str
    title: str
    artist: str
    album: str | None = None
    duration_ms: int
    cover_url: str | None = None
    preview_url: str | None = None
    release_year: int | None = None


class SpotifyPlaylist(_FrozenDto):
    spotify_id: str
    name: str
    description: str | None = None
    public: bool | None = None
    snapshot_id: str | None = None


class SpotifyQueue(_FrozenDto):
    currently_playing: SpotifyTrack | None = None
    queue: tuple[SpotifyTrack, ...] = ()


class SpotifyPlaybackState(_FrozenDto):
    is_playing: bool
    progress_ms: int | None = None
    device_id: str | None = None
    device_name: str | None = None
    track: SpotifyTrack | None = None


class TrackImport(_FrozenDto):
    spotify_id: str
    title: str
    artist: str
    album: str | None = None
    duration_seconds: int
    genre: str
    cover_url: str | None = None
    release_year: int | None = None


class PlaylistImport(_FrozenDto):
    spotify_playlist_id: str
    name: str
    track_spotify_ids: tuple[str, ...]


__all__ = [
    "PlaylistImport",
    "SpotifyPlaybackState",
    "SpotifyPlaylist",
    "SpotifyQueue",
    "SpotifyTokens",
    "SpotifyTrack",
    "TrackImport",
]
