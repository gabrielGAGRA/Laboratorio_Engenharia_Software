"""Unit tests for tracks_reviews router functions."""

from unittest.mock import MagicMock

from app.application.use_cases.review import (
    GetCommunityFeedUseCase,
    LikeReviewCommentUseCase,
)
from app.domain.models import ReviewComment
from app.presentation.routers.tracks_reviews import (
    get_community_feed,
    like_review,
)


def test_get_community_feed_accepts_custom_query_params() -> None:
    mock_use_case = MagicMock(spec=GetCommunityFeedUseCase)
    mock_use_case.execute.return_value = []

    res = get_community_feed(use_case=mock_use_case, days=14, limit=25)

    assert res == []
    mock_use_case.execute.assert_called_once_with(days=14, limit=25)


def test_get_community_feed_defaults() -> None:
    mock_use_case = MagicMock(spec=GetCommunityFeedUseCase)
    mock_use_case.execute.return_value = []

    res = get_community_feed(use_case=mock_use_case)

    assert res == []
    mock_use_case.execute.assert_called_once_with(days=5, limit=10)


def test_like_review_router_passes_review_and_user_id() -> None:
    mock_use_case = MagicMock(spec=LikeReviewCommentUseCase)
    review = ReviewComment(
        review_id=1,
        user_id=10,
        track_id=100,
        initial_rating=5,
        text="Awesome!",
        initial_likes_count=1,
    )
    mock_use_case.execute.return_value = review

    res = like_review(review_id=1, user_id=20, use_case=mock_use_case)

    assert res.review_id == 1
    assert res.likes_count == 1
    mock_use_case.execute.assert_called_once_with(review_id=1, user_id=20)
