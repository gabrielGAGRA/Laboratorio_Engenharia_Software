"""Use case for publishing a track review and comment."""

from typing import TYPE_CHECKING

from app.application.dtos.review_dtos import (
    PublishReviewInput,
    ReviewResponse,
)
from app.domain.exceptions import BusinessRuleViolationError, EntityNotFoundError
from app.domain.models.review import ReviewComment

if TYPE_CHECKING:
    from app.application.ports.repositories.review_repository import (
        ReviewRepositoryPort,
    )
    from app.application.ports.repositories.track_repository import TrackRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class PublishReviewUseCase:
    """Validates and persists a user review and numeric rating on a track."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        track_repo: TrackRepositoryPort,
        review_repo: ReviewRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._track_repo = track_repo
        self._review_repo = review_repo

    def execute(self, input_dto: PublishReviewInput) -> ReviewResponse:
        if not ReviewComment.is_valid_rating(input_dto.rating):
            raise BusinessRuleViolationError(
                f"Rating must be between {ReviewComment.MIN_RATING} and {ReviewComment.MAX_RATING}."
            )

        user = self._user_repo.find_by_id(input_dto.user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {input_dto.user_id} not found.")

        track = self._track_repo.find_by_id(input_dto.track_id)
        if not track or track.is_deleted:
            raise EntityNotFoundError(
                f"Track with ID {input_dto.track_id} not found or inactive."
            )

        review = ReviewComment(
            review_id=None,
            user_id=input_dto.user_id,
            track_id=input_dto.track_id,
            initial_rating=input_dto.rating,
            text=input_dto.text.strip() if input_dto.text else None,
            initial_likes_count=0,
            is_deleted=False,
        )
        saved = self._review_repo.save(review)
        return ReviewResponse.from_domain(saved)
