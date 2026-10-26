"""Use case for downvoting/skipping a track in a Jam queue."""

from typing import TYPE_CHECKING

from app.application.dtos.jam_dtos import (
    JamQueueItemResponse,
    VoteSkipJamTrackInput,
)
from app.domain.exceptions import BusinessRuleViolationError, EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.jam_repository import JamRepositoryPort
    from app.application.ports.repositories.track_repository import TrackRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class VoteSkipJamTrackUseCase:
    """Decrements vote points on a queued Jam track."""

    def __init__(
        self,
        jam_repo: JamRepositoryPort,
        user_repo: UserRepositoryPort,
        track_repo: TrackRepositoryPort,
    ) -> None:
        self._jam_repo = jam_repo
        self._user_repo = user_repo
        self._track_repo = track_repo

    def execute(self, input_dto: VoteSkipJamTrackInput) -> JamQueueItemResponse:
        user = self._user_repo.find_by_id(input_dto.user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {input_dto.user_id} not found.")

        jam = self._jam_repo.find_by_id(input_dto.jam_id)
        if not jam or not jam.is_active:
            raise EntityNotFoundError("Jam room not found or inactive.")

        track = self._track_repo.find_by_id(input_dto.track_id)
        if not track or track.is_deleted:
            raise EntityNotFoundError("Track not found or inactive.")

        if not user.can_listen(track):
            raise BusinessRuleViolationError(
                "Track is blocked for underage users or violates genre preferences."
            )

        item = self._jam_repo.find_queue_item(input_dto.jam_id, input_dto.track_id)
        if not item:
            raise EntityNotFoundError("Track is not currently in the jam queue.")

        item.vote(-1)
        saved = self._jam_repo.save_queue_item(item)
        return JamQueueItemResponse.from_domain(saved)
