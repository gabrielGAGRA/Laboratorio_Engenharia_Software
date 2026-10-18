"""Use case for advancing Jam playback to the top-voted queue track."""

from dataclasses import dataclass

from app.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    PermissionDeniedError,
)
lazy from app.application.ports.repositories.jam_repository import JamRepositoryPort
lazy from app.domain.models.jam import Jam


@dataclass(slots=True, frozen=True)
class AdvanceJamPlaybackUseCase:
    """Promotes the highest voted track in the queue to currently playing."""

    jam_repo: JamRepositoryPort

    def execute(self, jam_id: int, requester_user_id: int) -> Jam:
        jam = self.jam_repo.find_by_id(jam_id)
        if not jam or not jam.is_active:
            raise EntityNotFoundError("Jam room not found or inactive.")

        if not jam.is_host(requester_user_id):
            raise PermissionDeniedError("Only the jam host can advance playback.")

        queue = self.jam_repo.list_queue(jam_id)
        if not queue:
            raise BusinessRuleViolationError("No tracks in queue to advance.")

        winning_item = queue[0]
        return self.jam_repo.advance_playback(
            jam_id=jam_id,
            new_track_id=winning_item.track_id,
            removed_track_id=winning_item.track_id,
        )
