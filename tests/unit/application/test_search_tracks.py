"""Unit tests for SearchTracksUseCase pagination and filtering."""

from unittest.mock import MagicMock

import pytest

from app.application.dtos.review_dtos import SearchTracksInput
from app.application.use_cases.review.search_tracks import SearchTracksUseCase
from app.domain.models import Track, User


@pytest.fixture
def mock_user() -> User:
    user = MagicMock(spec=User)
    user.is_adult = True
    return user


def test_search_tracks_passes_pagination_to_repository(mock_user: User) -> None:
    user_repo = MagicMock()
    user_repo.find_by_id.return_value = mock_user

    track_repo = MagicMock()
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

    input_dto = SearchTracksInput(
        user_id=1,
        query="Queen",
        limit=25,
        offset=10,
    )

    result = use_case.execute(input_dto)

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
