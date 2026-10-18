"""Review presentation schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PublishReviewRequest(BaseModel):
    """Payload to post a star rating and critique on a track."""

    user_id: int
    track_id: int
    rating: int = Field(ge=1, le=5)
    text: str | None = Field(default=None, max_length=1000)


class ReviewResponse(BaseModel):
    """Public representation of a user review."""

    model_config = ConfigDict(from_attributes=True)

    review_id: int | None = None
    user_id: int
    track_id: int
    rating: int
    text: str | None = None
    likes_count: int = 0
    is_deleted: bool = False
    created_at: datetime | None = None


__all__ = [
    "PublishReviewRequest",
    "ReviewResponse",
]
