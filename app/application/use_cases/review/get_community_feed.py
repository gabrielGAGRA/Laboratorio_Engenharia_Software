"""Use case for retrieving top-liked recent community reviews."""

from typing import TYPE_CHECKING

from app.application.dtos.review_dtos import ReviewResponse

if TYPE_CHECKING:
    from app.application.ports.repositories.review_repository import (
        ReviewRepositoryPort,
    )


class GetCommunityFeedUseCase:
    """Returns the most liked reviews from the last given number of days."""

    def __init__(self, review_repo: ReviewRepositoryPort) -> None:
        self._review_repo = review_repo

    def execute(self, days: int = 5, limit: int = 3) -> list[ReviewResponse]:
        top_reviews = self._review_repo.list_top_recent(days=days, limit=limit)
        return [ReviewResponse.from_domain(r) for r in top_reviews]
