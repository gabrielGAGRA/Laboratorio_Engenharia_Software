"""Use case for advancing Jam playback to the top-voted queue track."""

from typing import TYPE_CHECKING

from app.application.dtos.jam_dtos import JamResponse
from app.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    PermissionDeniedError,
)

if TYPE_CHECKING:
    from app.application.ports.repositories.jam_repository import JamRepositoryPort


class AdvanceJamPlaybackUseCase:
    """Promotes the highest voted track in the queue to currently playing."""

    def __init__(self, jam_repo: JamRepositoryPort) -> None:
        self._jam_repo = jam_repo

    def execute(self, jam_id: int, requester_user_id: int) -> JamResponse:
        jam = self._jam_repo.find_by_id(jam_id)
        if not jam or not jam.is_active:
            raise EntityNotFoundError("Jam room not found or inactive.")

        if not jam.is_host(requester_user_id):
            raise PermissionDeniedError("Only the jam host can advance playback.")

        queue = self._jam_repo.list_queue(jam_id)
        if not queue:
            raise BusinessRuleViolationError("No tracks in queue to advance.")

        winning_item = queue[0]
        jam.set_current_track(winning_item.track_id)
        saved = self._jam_repo.save(jam)
        self._jam_repo.remove_track_from_queue(jam_id, winning_item.track_id)

        return JamResponse.from_domain(saved)
