"""Use case for publishing a track review and comment."""

from dataclasses import dataclass

from app.domain.exceptions import BusinessRuleViolationError, EntityNotFoundError
from app.domain.models.review import ReviewComment
lazy from app.application.commands.review_commands import PublishReviewCommand
lazy from app.application.ports.repositories.review_repository import (
    ReviewRepositoryPort,
)
lazy from app.application.ports.repositories.track_repository import TrackRepositoryPort
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort


@dataclass(slots=True, frozen=True)
class PublishReviewUseCase:
    """Validates and persists a user review and numeric rating on a track."""

    user_repo: UserRepositoryPort
    track_repo: TrackRepositoryPort
    review_repo: ReviewRepositoryPort

    def execute(self, command: PublishReviewCommand) -> ReviewComment:
        if not ReviewComment.is_valid_rating(command.rating):
            raise BusinessRuleViolationError(
                f"Rating must be between {ReviewComment.MIN_RATING} and {ReviewComment.MAX_RATING}."
            )

        user = self.user_repo.find_by_id(command.user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {command.user_id} not found.")

        track = self.track_repo.find_by_id(command.track_id)
        if not track or track.is_deleted:
            raise EntityNotFoundError(
                f"Track with ID {command.track_id} not found or inactive."
            )

        review = ReviewComment(
            review_id=None,
            user_id=command.user_id,
            track_id=command.track_id,
            initial_rating=command.rating,
            text=command.text.strip() if command.text else None,
            initial_likes_count=0,
            is_deleted=False,
        )
        return self.review_repo.save(review)
