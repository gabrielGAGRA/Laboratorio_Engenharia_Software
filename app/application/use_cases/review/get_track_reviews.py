"""Use case for listing all active reviews of a track."""

from typing import TYPE_CHECKING

from app.application.dtos.review_dtos import ReviewResponse
from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.review_repository import (
        ReviewRepositoryPort,
    )
    from app.application.ports.repositories.track_repository import TrackRepositoryPort


class GetTrackReviewsUseCase:
    """Retrieves all non-deleted reviews for a given music track."""

    def __init__(
        self,
        track_repo: TrackRepositoryPort,
        review_repo: ReviewRepositoryPort,
    ) -> None:
        self._track_repo = track_repo
        self._review_repo = review_repo

    def execute(self, track_id: int, limit: int = 50) -> list[ReviewResponse]:
        track = self._track_repo.find_by_id(track_id)
        if not track or track.is_deleted:
            raise EntityNotFoundError("Track not found or inactive.")

        reviews = self._review_repo.list_by_track(track_id, limit=limit)
        return [ReviewResponse.from_domain(r) for r in reviews]
