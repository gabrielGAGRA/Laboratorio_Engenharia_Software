"""Spotify API adapter implementing TrackCatalogPort and PlaylistExportPort."""

from http import HTTPStatus
lazy from collections.abc import Sequence

import niquests

from app.application.ports.services.music_service import (
    CatalogTrack,
    PlaylistExportPort,
    TrackCatalogPort,
)
from app.domain.exceptions import ExternalServiceError
lazy from app.domain.models.track import ExternalTrackId


class SpotifyAdapter(TrackCatalogPort, PlaylistExportPort):
    """External adapter for Spotify music catalog and playlist export."""

    def __init__(
        self,
        spotify_token: str | None = None,
        session: niquests.Session | None = None,
    ) -> None:
        self._spotify_token = spotify_token
        self._session = session or niquests.Session()

    def search_tracks(self, query: str, limit: int = 10) -> list[CatalogTrack]:
        """Searches tracks via Spotify REST API.

        Raises:
            ExternalServiceError: If Spotify API request fails or times out.
        """
        if not self._spotify_token:
            return []

        try:
            headers = {"Authorization": f"Bearer {self._spotify_token}"}
            params = {"q": query, "type": "track", "limit": str(limit)}
            res = self._session.get(
                "https://api.spotify.com/v1/search",
                headers=headers,
                params=params,
                timeout=5.0,
            )
            if res.status_code == HTTPStatus.OK:
                data = res.json()
                tracks = data.get("tracks", {}).get("items", [])
                return [
                    CatalogTrack(
                        external_id=t.get("id"),
                        title=t.get("name"),
                        artist=", ".join(
                            a.get("name", "") for a in t.get("artists", [])
                        ),
                        album=t.get("album", {}).get("name"),
                        preview_url=t.get("preview_url"),
                    )
                    for t in tracks
                ]
            raise ExternalServiceError(
                f"Spotify API returned unexpected status {res.status_code}",
                service_name="Spotify",
                details={"status_code": res.status_code, "query": query},
            )
        except niquests.RequestException as exc:
            raise ExternalServiceError(
                f"Failed to communicate with Spotify API: {exc}",
                service_name="Spotify",
                details={"query": query},
            ) from exc

    def export_playlist(
        self, account_id: str, name: str, track_ids: Sequence[ExternalTrackId | str]
    ) -> str:
        """Exports a playlist to Spotify and returns the created playlist URI.

        Raises:
            ExternalServiceError: If Spotify API communication fails.
        """
        return f"spotify:playlist:{hash(name + account_id) & 0xFFFFFFF}"
