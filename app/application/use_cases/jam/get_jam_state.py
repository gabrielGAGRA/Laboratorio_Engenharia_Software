"""Use case for retrieving current Jam state, queue, and playback."""

from typing import TYPE_CHECKING

from app.application.dtos.jam_dtos import (
    JamQueueItemResponse,
    JamResponse,
    JamStateResponse,
)
from app.application.dtos.track_dtos import TrackResponse
from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.jam_repository import JamRepositoryPort
    from app.application.ports.repositories.track_repository import TrackRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class GetJamStateUseCase:
    """Returns room state, currently playing track, and ordered queue."""

    def __init__(
        self,
        jam_repo: JamRepositoryPort,
        user_repo: UserRepositoryPort,
        track_repo: TrackRepositoryPort,
    ) -> None:
        self._jam_repo = jam_repo
        self._user_repo = user_repo
        self._track_repo = track_repo

    def execute(self, jam_id: int, user_id: int) -> JamStateResponse:
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        jam = self._jam_repo.find_by_id(jam_id)
        if not jam:
            raise EntityNotFoundError(f"Jam session {jam_id} not found.")

        raw_queue = self._jam_repo.list_queue(jam_id)
        current_track_domain = None
        if jam.current_track_id:
            current_track_domain = self._track_repo.find_by_id(jam.current_track_id)

        queue_items: list[JamQueueItemResponse] = []
        for item in raw_queue:
            track = self._track_repo.find_by_id(item.track_id)
            if not track or track.is_deleted:
                continue
            if not user.is_adult and track.explicit:
                continue
            queue_items.append(JamQueueItemResponse.from_domain(item))

        current_track_dto = None
        if (
            current_track_domain
            and not current_track_domain.is_deleted
            and (user.is_adult or not current_track_domain.explicit)
        ):
            current_track_dto = TrackResponse.from_domain(current_track_domain)

        return JamStateResponse(
            jam=JamResponse.from_domain(jam),
            current_track=current_track_dto,
            queue=queue_items,
        )
