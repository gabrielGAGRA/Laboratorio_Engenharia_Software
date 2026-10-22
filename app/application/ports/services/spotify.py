"""Application ports for the Spotify Web API capabilities."""

from collections.abc import Sequence
from typing import Protocol

from app.application.dtos.spotify_dtos import (
    SpotifyPlaybackState,
    SpotifyPlaylist,
    SpotifyQueue,
    SpotifyTokens,
    SpotifyTrack,
)


class SpotifyAuthPort(Protocol):
    def get_authorize_url(self, scopes: Sequence[str], state: str) -> str: ...

    def exchange_code(self, code: str) -> SpotifyTokens: ...

    def refresh_access_token(self) -> SpotifyTokens: ...

    def get_client_credentials_token(self) -> SpotifyTokens: ...


class SpotifyCatalogPort(Protocol):
    def search_tracks(
        self, query: str, limit: int = 5, offset: int = 0, market: str | None = None
    ) -> list[SpotifyTrack]: ...

    def get_track(self, track_id: str, market: str | None = None) -> SpotifyTrack: ...


class SpotifyPlaylistsPort(Protocol):
    def get_my_playlists(
        self, limit: int = 20, offset: int = 0
    ) -> list[SpotifyPlaylist]: ...

    def create_playlist(
        self,
        name: str,
        *,
        public: bool = False,
        collaborative: bool = False,
        description: str | None = None,
    ) -> SpotifyPlaylist: ...

    def update_playlist_details(
        self,
        playlist_id: str,
        *,
        name: str | None = None,
        public: bool | None = None,
        collaborative: bool | None = None,
        description: str | None = None,
    ) -> None: ...

    def get_playlist(
        self, playlist_id: str, market: str | None = None
    ) -> SpotifyPlaylist: ...

    def get_playlist_items(
        self,
        playlist_id: str,
        limit: int = 50,
        offset: int = 0,
        market: str | None = None,
    ) -> list[SpotifyTrack]: ...

    def add_playlist_items(
        self, playlist_id: str, uris: Sequence[str], position: int | None = None
    ) -> str: ...

    def update_playlist_items(  # noqa: PLR0913
        self,
        playlist_id: str,
        *,
        uris: Sequence[str] | None = None,
        range_start: int | None = None,
        insert_before: int | None = None,
        range_length: int | None = None,
        snapshot_id: str | None = None,
    ) -> str | None: ...

    def remove_playlist_items(
        self, playlist_id: str, uris: Sequence[str], snapshot_id: str | None = None
    ) -> str: ...

    def get_playlist_cover(self, playlist_id: str) -> list[str]: ...

    def upload_playlist_cover(self, playlist_id: str, base64_jpeg: str) -> None: ...


class SpotifyQueuePort(Protocol):
    def get_playback_state(
        self, market: str | None = None
    ) -> SpotifyPlaybackState | None: ...

    def get_queue(self) -> SpotifyQueue: ...

    def add_to_queue(self, uri: str, device_id: str | None = None) -> None: ...

    def next_track(self, device_id: str | None = None) -> None: ...

    def previous_track(self, device_id: str | None = None) -> None: ...

    def seek(self, position_ms: int, device_id: str | None = None) -> None: ...

    def play(  # noqa: PLR0913
        self,
        *,
        context_uri: str | None = None,
        uris: Sequence[str] | None = None,
        offset: int | None = None,
        position_ms: int | None = None,
        device_id: str | None = None,
    ) -> None: ...

    def pause(self, device_id: str | None = None) -> None: ...


__all__ = [
    "SpotifyAuthPort",
    "SpotifyCatalogPort",
    "SpotifyPlaylistsPort",
    "SpotifyQueuePort",
]
