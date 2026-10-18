"""Composite music service adapter combining Spotify and iTunes adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    import niquests

    from app.domain.types import ExternalTrackId

from app.application.ports.services.music_service import (
    CatalogTrack,
    PlaylistExportPort,
    TrackCatalogPort,
    TrackPreview,
    TrackPreviewPort,
)
from app.infrastructure.adapters.itunes.itunes_adapter import ITunesAdapter
from app.infrastructure.adapters.spotify.spotify_adapter import SpotifyAdapter


class ExternalMusicServiceAdapter(
    TrackCatalogPort, TrackPreviewPort, PlaylistExportPort
):
    """Composite adapter implementing catalog, preview, and export ports."""

    def __init__(
        self,
        spotify_token: str | None = None,
        session: niquests.Session | None = None,
    ) -> None:
        self._spotify = SpotifyAdapter(spotify_token=spotify_token, session=session)
        self._itunes = ITunesAdapter(session=session)

    def search_tracks(self, query: str, limit: int = 10) -> list[CatalogTrack]:
        return self._spotify.search_tracks(query=query, limit=limit)

    def find_preview(self, term: str) -> TrackPreview | None:
        return self._itunes.find_preview(term=term)

    def export_playlist(
        self, account_id: str, name: str, track_ids: Sequence[ExternalTrackId | str]
    ) -> str:
        return self._spotify.export_playlist(
            account_id=account_id, name=name, track_ids=track_ids
        )


__all__ = ["ExternalMusicServiceAdapter"]
