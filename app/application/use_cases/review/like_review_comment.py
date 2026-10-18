"""Use case for liking a review comment."""

from typing import TYPE_CHECKING

from app.application.dtos.review_dtos import ReviewResponse
from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.review_repository import (
        ReviewRepositoryPort,
    )


class LikeReviewCommentUseCase:
    """Increments the like counter of a community review comment."""

    def __init__(self, review_repo: ReviewRepositoryPort) -> None:
        self._review_repo = review_repo

    def execute(self, review_id: int) -> ReviewResponse:
        review = self._review_repo.find_by_id(review_id)
        if not review or review.is_deleted:
            raise EntityNotFoundError("Review not found or deleted.")

        review.like()
        saved = self._review_repo.save(review)
        return ReviewResponse.from_domain(saved)
