"""Use case: feed the track catalog table from a Spotify search."""

from app.application.ports.repositories.spotify_import import TrackRepository
from app.application.ports.services.spotify import SpotifyCatalogPort
from app.application.use_cases.spotify.helpers import to_track_import

DEFAULT_GENRE = "Desconhecido"


class SyncTracksFromSpotify:
    """Spotify exposes no track genre in Development mode, so ``default_genre`` fills it."""

    def __init__(
        self,
        catalog: SpotifyCatalogPort,
        tracks: TrackRepository,
        default_genre: str = DEFAULT_GENRE,
    ) -> None:
        self._catalog = catalog
        self._tracks = tracks
        self._default_genre = default_genre

    def execute(self, query: str, limit: int = 10, offset: int = 0) -> int:
        found = self._catalog.search_tracks(query, limit=limit, offset=offset)
        for track in found:
            self._tracks.upsert_by_spotify_id(
                to_track_import(track, self._default_genre)
            )
        return len(found)
