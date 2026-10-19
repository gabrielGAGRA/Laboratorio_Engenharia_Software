"""Unit tests for AddTrackToPlaylistUseCase."""

from unittest.mock import MagicMock

import pytest

from app.application.commands.playlist_commands import AddTrackToPlaylistCommand
from app.application.ports.repositories.playlist_repository import (
    PlaylistRepositoryPort,
)
from app.application.ports.repositories.track_repository import TrackRepositoryPort
from app.application.ports.repositories.user_repository import UserRepositoryPort
from app.application.use_cases.playlist.add_track_to_playlist import (
    AddTrackToPlaylistUseCase,
)
from app.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    PermissionDeniedError,
)
from app.domain.models.playlist import Playlist
from app.domain.models.track import Track
from app.domain.models.user import User


def test_add_track_to_playlist_success_appends_and_saves_playlist() -> None:
    user = User(
        user_id=1,
        email="owner@ribbit.com",
        password_hash="pw",
        display_name="Owner",
        age=25,
        plan_id=1,
    )
    playlist = Playlist(
        playlist_id=10,
        user_id=1,
        name="Road Trip",
    )
    track = Track(
        track_id=100,
        title="Highway Hop",
        artist="Toads",
        duration_seconds=210,
        genre="Rock",
    )

    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = user

    playlist_repo = MagicMock(spec=PlaylistRepositoryPort)
    playlist_repo.find_by_id.return_value = playlist
    playlist_repo.save.side_effect = lambda p: p

    track_repo = MagicMock(spec=TrackRepositoryPort)
    track_repo.find_by_id.return_value = track

    use_case = AddTrackToPlaylistUseCase(
        user_repo=user_repo,
        track_repo=track_repo,
        playlist_repo=playlist_repo,
    )
    command = AddTrackToPlaylistCommand(playlist_id=10, track_id=100, user_id=1)

    result = use_case.execute(command)

    assert result is playlist
    assert result.tracks == (track,)
    playlist_repo.save.assert_called_once_with(playlist)


def test_add_track_to_playlist_idor_non_owner_raises_permission_denied() -> None:
    intruder = User(
        user_id=99,
        email="intruder@ribbit.com",
        password_hash="pw",
        display_name="Intruder",
        age=25,
        plan_id=1,
    )
    playlist = Playlist(
        playlist_id=10,
        user_id=1,
        name="Victim Playlist",
    )

    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = intruder

    playlist_repo = MagicMock(spec=PlaylistRepositoryPort)
    playlist_repo.find_by_id.return_value = playlist

    track_repo = MagicMock(spec=TrackRepositoryPort)

    use_case = AddTrackToPlaylistUseCase(
        user_repo=user_repo,
        track_repo=track_repo,
        playlist_repo=playlist_repo,
    )
    command = AddTrackToPlaylistCommand(playlist_id=10, track_id=100, user_id=99)

    with pytest.raises(
        PermissionDeniedError, match="playlist does not belong to this user"
    ):
        use_case.execute(command)

    track_repo.find_by_id.assert_not_called()
    playlist_repo.save.assert_not_called()


def test_add_track_to_playlist_minor_blocked_from_explicit_track() -> None:
    minor = User(
        user_id=1,
        email="minor@ribbit.com",
        password_hash="pw",
        display_name="Minor",
        age=14,
        plan_id=1,
    )
    playlist = Playlist(playlist_id=10, user_id=1, name="My Mix")
    explicit_track = Track(
        track_id=100,
        title="Explicit Song",
        artist="Artist",
        duration_seconds=200,
        genre="Pop",
        explicit=True,
    )

    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = minor

    playlist_repo = MagicMock(spec=PlaylistRepositoryPort)
    playlist_repo.find_by_id.return_value = playlist

    track_repo = MagicMock(spec=TrackRepositoryPort)
    track_repo.find_by_id.return_value = explicit_track

    use_case = AddTrackToPlaylistUseCase(
        user_repo=user_repo,
        track_repo=track_repo,
        playlist_repo=playlist_repo,
    )
    command = AddTrackToPlaylistCommand(playlist_id=10, track_id=100, user_id=1)

    with pytest.raises(BusinessRuleViolationError, match="underage"):
        use_case.execute(command)

    playlist_repo.save.assert_not_called()


def test_add_track_to_playlist_duplicate_track_raises_business_rule_error() -> None:
    user = User(
        user_id=1,
        email="owner@ribbit.com",
        password_hash="pw",
        display_name="Owner",
        age=25,
        plan_id=1,
    )
    track = Track(
        track_id=100,
        title="Highway Hop",
        artist="Toads",
        duration_seconds=210,
        genre="Rock",
    )
    playlist = Playlist(
        playlist_id=10,
        user_id=1,
        name="Road Trip",
        initial_tracks=[track],
    )

    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = user

    playlist_repo = MagicMock(spec=PlaylistRepositoryPort)
    playlist_repo.find_by_id.return_value = playlist

    track_repo = MagicMock(spec=TrackRepositoryPort)
    track_repo.find_by_id.return_value = track

    use_case = AddTrackToPlaylistUseCase(
        user_repo=user_repo,
        track_repo=track_repo,
        playlist_repo=playlist_repo,
    )
    command = AddTrackToPlaylistCommand(playlist_id=10, track_id=100, user_id=1)

    with pytest.raises(BusinessRuleViolationError, match="already in the playlist"):
        use_case.execute(command)

    playlist_repo.save.assert_not_called()


def test_add_track_to_playlist_user_not_found_raises_entity_not_found() -> None:
    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = None

    use_case = AddTrackToPlaylistUseCase(
        user_repo=user_repo,
        track_repo=MagicMock(spec=TrackRepositoryPort),
        playlist_repo=MagicMock(spec=PlaylistRepositoryPort),
    )
    command = AddTrackToPlaylistCommand(playlist_id=10, track_id=100, user_id=999)

    with pytest.raises(EntityNotFoundError, match="User with ID 999 not found"):
        use_case.execute(command)


def test_add_track_to_playlist_playlist_not_found_raises_entity_not_found() -> None:
    user = User(
        user_id=1,
        email="owner@ribbit.com",
        password_hash="pw",
        display_name="Owner",
        age=25,
        plan_id=1,
    )
    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = user

    playlist_repo = MagicMock(spec=PlaylistRepositoryPort)
    playlist_repo.find_by_id.return_value = None

    use_case = AddTrackToPlaylistUseCase(
        user_repo=user_repo,
        track_repo=MagicMock(spec=TrackRepositoryPort),
        playlist_repo=playlist_repo,
    )
    command = AddTrackToPlaylistCommand(playlist_id=404, track_id=100, user_id=1)

    with pytest.raises(EntityNotFoundError, match="Playlist with ID 404 not found"):
        use_case.execute(command)


def test_add_track_to_playlist_deleted_track_raises_entity_not_found() -> None:
    user = User(
        user_id=1,
        email="owner@ribbit.com",
        password_hash="pw",
        display_name="Owner",
        age=25,
        plan_id=1,
    )
    playlist = Playlist(playlist_id=10, user_id=1, name="Road Trip")
    deleted_track = Track(
        track_id=100,
        title="Deleted",
        artist="Artist",
        duration_seconds=180,
        genre="Rock",
        is_deleted=True,
    )

    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = user

    playlist_repo = MagicMock(spec=PlaylistRepositoryPort)
    playlist_repo.find_by_id.return_value = playlist

    track_repo = MagicMock(spec=TrackRepositoryPort)
    track_repo.find_by_id.return_value = deleted_track

    use_case = AddTrackToPlaylistUseCase(
        user_repo=user_repo,
        track_repo=track_repo,
        playlist_repo=playlist_repo,
    )
    command = AddTrackToPlaylistCommand(playlist_id=10, track_id=100, user_id=1)

    with pytest.raises(
        EntityNotFoundError, match="Track with ID 100 not found or inactive"
    ):
        use_case.execute(command)
