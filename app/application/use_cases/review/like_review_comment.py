"""Use case for liking a review comment."""

from dataclasses import dataclass

from app.domain.exceptions import EntityNotFoundError
lazy from app.application.ports.repositories.review_repository import (
    ReviewRepositoryPort,
)
lazy from app.domain.models.review import ReviewComment


@dataclass(slots=True, frozen=True)
class LikeReviewCommentUseCase:
    """Increments the like counter of a community review comment."""

    review_repo: ReviewRepositoryPort

    def execute(self, review_id: int) -> ReviewComment:
        review = self.review_repo.find_by_id(review_id)
        if not review or review.is_deleted:
            raise EntityNotFoundError("Review not found or deleted.")

        review.like()
        return self.review_repo.save(review)
