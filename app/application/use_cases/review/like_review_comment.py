"""Use case for liking a review comment."""

from dataclasses import dataclass

from app.domain.exceptions import BusinessRuleViolationError, EntityNotFoundError
lazy from app.application.ports.repositories.review_repository import (
    ReviewRepositoryPort,
)
lazy from app.domain.models.review import ReviewComment


@dataclass(slots=True, frozen=True)
class LikeReviewCommentUseCase:
    """Increments the like counter of a community review comment."""

    review_repo: ReviewRepositoryPort

    def execute(self, review_id: int, user_id: int) -> ReviewComment:
        review = self.review_repo.find_by_id(review_id)
        if not review or review.is_deleted:
            raise EntityNotFoundError("Review not found or deleted.")

        if self.review_repo.has_user_liked(review_id, user_id):
            raise BusinessRuleViolationError("User has already liked this review.")

        review.like()
        saved = self.review_repo.save(review)
        self.review_repo.record_like(review_id, user_id)
        return saved
