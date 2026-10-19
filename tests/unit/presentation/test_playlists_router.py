"""Unit tests for playlists router functions."""

from unittest.mock import MagicMock

from app.application.commands import (
    AddTrackToPlaylistCommand,
    CreateDeckPlaylistCommand,
)
from app.application.use_cases.playlist import (
    AddTrackToPlaylistUseCase,
    CreateDeckPlaylistUseCase,
    ExportPlaylistToSpotifyUseCase,
    ListUserPlaylistsUseCase,
)
from app.domain.models import Playlist, Track
from app.presentation.routers.playlists import (
    create_deck_playlist,
    export_playlist_to_spotify,
    list_playlists,
    swipe_add_track,
)
from app.presentation.schemas import (
    DeckPlaylistRequest,
    SwipeAddTrackRequest,
)


def test_create_deck_playlist_forwards_command_and_returns_playlist() -> None:
    mock_use_case = MagicMock(spec=CreateDeckPlaylistUseCase)
    track = Track(
        track_id=1,
        title="Track 1",
        artist="Artist 1",
        duration_seconds=180,
        genre="rock",
    )
    playlist = Playlist(
        playlist_id=10,
        user_id=3,
        name="Roadtrip Deck",
        description="Energetic rock",
        initial_tracks=[track],
    )
    mock_use_case.execute.return_value = playlist
    req = DeckPlaylistRequest(
        user_id=3,
        name="Roadtrip Deck",
        duration_minutes=30,
        genre="rock",
        year=2020,
        artist="Artist 1",
        country="US",
        description="Energetic rock",
    )

    res = create_deck_playlist(req=req, use_case=mock_use_case)

    assert res.playlist_id == 10
    assert res.user_id == 3
    assert res.name == "Roadtrip Deck"
    assert len(res.tracks) == 1
    assert res.tracks[0].track_id == 1
    mock_use_case.execute.assert_called_once_with(
        CreateDeckPlaylistCommand(
            user_id=3,
            name="Roadtrip Deck",
            duration_minutes=30,
            genre="rock",
            year=2020,
            artist="Artist 1",
            country="US",
            description="Energetic rock",
        )
    )


def test_swipe_add_track_executes_command_and_returns_success() -> None:
    mock_use_case = MagicMock(spec=AddTrackToPlaylistUseCase)
    req = SwipeAddTrackRequest(track_id=99)

    res = swipe_add_track(
        playlist_id=10,
        req=req,
        user_id=3,
        use_case=mock_use_case,
    )

    assert res.success is True
    mock_use_case.execute.assert_called_once_with(
        AddTrackToPlaylistCommand(
            playlist_id=10,
            track_id=99,
            user_id=3,
        )
    )


def test_list_playlists_returns_mapped_user_playlists() -> None:
    mock_use_case = MagicMock(spec=ListUserPlaylistsUseCase)
    playlist = Playlist(
        playlist_id=11,
        user_id=3,
        name="My Favorites",
    )
    mock_use_case.execute.return_value = [playlist]

    res = list_playlists(user_id=3, use_case=mock_use_case)

    assert len(res) == 1
    assert res[0].playlist_id == 11
    assert res[0].name == "My Favorites"
    mock_use_case.execute.assert_called_once_with(user_id=3)


def test_export_playlist_to_spotify_returns_updated_playlist() -> None:
    mock_use_case = MagicMock(spec=ExportPlaylistToSpotifyUseCase)
    playlist = Playlist(
        playlist_id=11,
        user_id=3,
        name="My Favorites",
        spotify_playlist_id="sp_playlist_123",
        is_exported=True,
    )
    mock_use_case.execute.return_value = playlist

    res = export_playlist_to_spotify(
        playlist_id=11,
        user_id=3,
        use_case=mock_use_case,
    )

    assert res.playlist_id == 11
    assert res.is_exported is True
    assert res.spotify_playlist_id == "sp_playlist_123"
    mock_use_case.execute.assert_called_once_with(
        user_id=3,
        playlist_id=11,
    )
