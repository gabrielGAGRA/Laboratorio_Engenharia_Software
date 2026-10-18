"""Use case for retrieving top-liked reviews for administrative moderation."""

from typing import TYPE_CHECKING

from app.application.dtos.review_dtos import ReviewResponse

if TYPE_CHECKING:
    from app.application.ports.repositories.review_repository import (
        ReviewRepositoryPort,
    )


class GetTopModerationReviewsUseCase:
    """Returns top liked reviews from the last 30 days for content moderation."""

    def __init__(self, review_repo: ReviewRepositoryPort) -> None:
        self._review_repo = review_repo

    def execute(self) -> list[ReviewResponse]:
        top = self._review_repo.list_top_recent(days=30, limit=10)
        return [ReviewResponse.from_domain(r) for r in top]
