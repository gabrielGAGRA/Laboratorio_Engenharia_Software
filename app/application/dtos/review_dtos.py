"""Data transfer objects for reviews and community feed."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from app.domain.models.review import ReviewComment


@dataclass(slots=True, frozen=True, kw_only=True)
class SearchTracksInput:
    user_id: int
    artist: str | None = None
    album: str | None = None
    genre: str | None = None
    year: int | None = None
    query: str | None = None
    limit: int = 50
    offset: int = 0


@dataclass(slots=True, frozen=True, kw_only=True)
class PublishReviewInput:
    user_id: int
    track_id: int
    rating: int
    text: str | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class ReviewResponse:
    review_id: int | None
    user_id: int
    track_id: int
    rating: int
    text: str | None
    likes_count: int
    is_deleted: bool
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, review: ReviewComment) -> ReviewResponse:
        return cls(
            review_id=review.review_id,
            user_id=review.user_id,
            track_id=review.track_id,
            rating=review.rating,
            text=review.text,
            likes_count=review.likes_count,
            is_deleted=review.is_deleted,
            created_at=review.created_at,
        )
