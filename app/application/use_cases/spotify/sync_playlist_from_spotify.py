"""Use case: import a Spotify playlist and its tracks into the database."""

from app.application.dtos.spotify_dtos import PlaylistImport, SpotifyTrack
from app.application.ports.repositories.spotify_import import (
    PlaylistRepository,
    TrackRepository,
)
from app.application.ports.services.spotify import SpotifyPlaylistsPort
from app.application.use_cases.spotify.helpers import to_track_import
from app.application.use_cases.spotify.sync_tracks_from_spotify import DEFAULT_GENRE

_PAGE_SIZE = 50
_DEFAULT_MAX_ITEMS = 100


class SyncPlaylistFromSpotify:
    """``max_items`` bounds API calls: there are no batch routes and quota is shared."""

    def __init__(  # noqa: PLR0913
        self,
        playlists: SpotifyPlaylistsPort,
        tracks: TrackRepository,
        playlist_repository: PlaylistRepository,
        default_genre: str = DEFAULT_GENRE,
        max_items: int = _DEFAULT_MAX_ITEMS,
    ) -> None:
        self._playlists = playlists
        self._tracks = tracks
        self._playlist_repository = playlist_repository
        self._default_genre = default_genre
        self._max_items = max_items

    def execute(self, spotify_playlist_id: str) -> int:
        playlist = self._playlists.get_playlist(spotify_playlist_id)
        collected = self._collect_items(spotify_playlist_id)
        for track in collected:
            self._tracks.upsert_by_spotify_id(
                to_track_import(track, self._default_genre)
            )
        self._playlist_repository.save_imported(
            PlaylistImport(
                spotify_playlist_id=playlist.spotify_id,
                name=playlist.name,
                track_spotify_ids=tuple(track.spotify_id for track in collected),
            )
        )
        return len(collected)

    def _collect_items(self, spotify_playlist_id: str) -> list[SpotifyTrack]:
        collected: list[SpotifyTrack] = []
        while len(collected) < self._max_items:
            limit = min(_PAGE_SIZE, self._max_items - len(collected))
            page = self._playlists.get_playlist_items(
                spotify_playlist_id, limit=limit, offset=len(collected)
            )
            collected.extend(page)
            if len(page) < limit:
                break
        return collected
