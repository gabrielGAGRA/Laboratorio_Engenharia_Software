"""Unit tests for the Spotify database-feeding use cases."""

from collections.abc import Sequence

import pytest

from app.application.dtos.spotify_dtos import (
    PlaylistImport,
    SpotifyPlaylist,
    SpotifyTrack,
    TrackImport,
)
from app.application.use_cases.spotify.sync_playlist_from_spotify import (
    SyncPlaylistFromSpotify,
)
from app.application.use_cases.spotify.sync_tracks_from_spotify import (
    SyncTracksFromSpotify,
)


def _track(track_id: str, duration_ms: int = 200_000) -> SpotifyTrack:
    return SpotifyTrack(
        spotify_id=track_id,
        uri=f"spotify:track:{track_id}",
        title=f"T{track_id}",
        artist="Art",
        album="Alb",
        duration_ms=duration_ms,
        cover_url="http://c",
        release_year=2020,
    )


class FakeCatalog:
    def __init__(self, tracks: Sequence[SpotifyTrack]) -> None:
        self.tracks = list(tracks)
        self.queries: list[tuple[str, int, int]] = []

    def search_tracks(
        self, query: str, limit: int = 5, offset: int = 0, market: str | None = None
    ) -> list[SpotifyTrack]:
        self.queries.append((query, limit, offset))
        return self.tracks


class FakePlaylists:
    def __init__(self, pages: Sequence[list[SpotifyTrack]]) -> None:
        self.pages = list(pages)
        self.offsets: list[int] = []

    def get_playlist(
        self, playlist_id: str, market: str | None = None
    ) -> SpotifyPlaylist:
        return SpotifyPlaylist(spotify_id=playlist_id, name="Mix")

    def get_playlist_items(
        self,
        playlist_id: str,
        limit: int = 50,
        offset: int = 0,
        market: str | None = None,
    ) -> list[SpotifyTrack]:
        self.offsets.append(offset)
        index = offset // limit
        return self.pages[index] if index < len(self.pages) else []


class FakeTrackRepository:
    def __init__(self) -> None:
        self.saved: list[TrackImport] = []

    def upsert_by_spotify_id(self, track: TrackImport) -> None:
        self.saved.append(track)


class FakePlaylistRepository:
    def __init__(self) -> None:
        self.saved: list[PlaylistImport] = []

    def save_imported(self, playlist: PlaylistImport) -> None:
        self.saved.append(playlist)


@pytest.mark.unit
class TestSyncTracks:
    def test_upserts_mapped_tracks_with_default_genre(self) -> None:
        catalog = FakeCatalog([_track("1", 200_400), _track("2", 100)])
        repo = FakeTrackRepository()

        count = SyncTracksFromSpotify(catalog, repo).execute(
            "daft punk", limit=2, offset=4
        )

        assert count == 2
        assert catalog.queries == [("daft punk", 2, 4)]
        first, second = repo.saved
        assert first == TrackImport(
            spotify_id="1",
            title="T1",
            artist="Art",
            album="Alb",
            duration_seconds=200,
            genre="Desconhecido",
            cover_url="http://c",
            release_year=2020,
        )
        assert second.duration_seconds == 1

    def test_custom_default_genre(self) -> None:
        repo = FakeTrackRepository()
        SyncTracksFromSpotify(
            FakeCatalog([_track("1")]), repo, default_genre="Pop"
        ).execute("x")
        assert repo.saved[0].genre == "Pop"


@pytest.mark.unit
class TestSyncPlaylist:
    def test_saves_tracks_then_playlist_across_pages(self) -> None:
        playlists = FakePlaylists([[_track(str(i)) for i in range(50)], [_track("x")]])
        tracks, saved = FakeTrackRepository(), FakePlaylistRepository()

        count = SyncPlaylistFromSpotify(playlists, tracks, saved).execute("p1")

        assert count == 51
        assert playlists.offsets == [0, 50]
        assert len(tracks.saved) == 51
        assert saved.saved[0].spotify_playlist_id == "p1"
        assert saved.saved[0].name == "Mix"
        assert saved.saved[0].track_spotify_ids[-1] == "x"

    def test_stops_at_max_items(self) -> None:
        playlists = FakePlaylists([[_track(str(i)) for i in range(50)]] * 3)
        tracks, saved = FakeTrackRepository(), FakePlaylistRepository()

        count = SyncPlaylistFromSpotify(playlists, tracks, saved, max_items=50).execute(
            "p1"
        )

        assert count == 50
        assert playlists.offsets == [0]
