"""Unit tests for SearchTracksUseCase pagination, filtering, and age gates."""

from unittest.mock import MagicMock

import pytest

from app.application.commands import SearchTracksCommand
from app.application.ports.repositories.track_repository import TrackRepositoryPort
from app.application.ports.repositories.user_repository import UserRepositoryPort
from app.application.use_cases.review.search_tracks import SearchTracksUseCase
from app.domain.exceptions import EntityNotFoundError
from app.domain.models import Track, User


@pytest.fixture
def mock_user() -> User:
    user = MagicMock(spec=User)
    user.is_adult = True
    return user


def test_search_tracks_passes_pagination_to_repository(mock_user: User) -> None:
    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = mock_user

    track_repo = MagicMock(spec=TrackRepositoryPort)
    track_repo.find_by_filters.return_value = [
        Track(
            track_id=1,
            title="Bohemian Rhapsody",
            artist="Queen",
            duration_seconds=354,
            genre="Rock",
        )
    ]

    use_case = SearchTracksUseCase(user_repo=user_repo, track_repo=track_repo)

    command = SearchTracksCommand(
        user_id=1,
        query="Queen",
        limit=25,
        offset=10,
    )

    result = use_case.execute(command)

    assert len(result) == 1
    assert result[0].title == "Bohemian Rhapsody"
    track_repo.find_by_filters.assert_called_once_with(
        artist=None,
        album=None,
        genre=None,
        year=None,
        query="Queen",
        limit=25,
        offset=10,
    )


def test_search_tracks_filters_explicit_tracks_for_underage_user() -> None:
    minor_user = User(
        user_id=2,
        email="minor@ribbit.com",
        password_hash="pw",
        display_name="Minor",
        age=16,
        plan_id=1,
    )
    clean_track = Track(
        track_id=1,
        title="Clean Song",
        artist="Artist",
        duration_seconds=200,
        genre="Pop",
        explicit=False,
    )
    explicit_track = Track(
        track_id=2,
        title="Explicit Song",
        artist="Artist",
        duration_seconds=200,
        genre="Pop",
        explicit=True,
    )

    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = minor_user

    track_repo = MagicMock(spec=TrackRepositoryPort)
    track_repo.find_by_filters.return_value = [clean_track, explicit_track]

    use_case = SearchTracksUseCase(user_repo=user_repo, track_repo=track_repo)
    command = SearchTracksCommand(
        user_id=2,
        artist="Artist",
        album="Album",
        genre="Pop",
        year=2024,
    )

    result = use_case.execute(command)

    assert result == [clean_track]


def test_search_tracks_user_not_found_raises_entity_not_found() -> None:
    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = None
    track_repo = MagicMock(spec=TrackRepositoryPort)

    use_case = SearchTracksUseCase(user_repo=user_repo, track_repo=track_repo)
    command = SearchTracksCommand(user_id=999, query="anything")

    with pytest.raises(EntityNotFoundError, match="User with ID 999 not found"):
        use_case.execute(command)

    track_repo.find_by_filters.assert_not_called()
