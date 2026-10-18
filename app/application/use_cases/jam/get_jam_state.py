"""Use case for retrieving current Jam state, queue, and playback."""

from dataclasses import dataclass

from app.application.dtos.jam_dtos import JamStateResult
from app.domain.exceptions import EntityNotFoundError
lazy from app.application.ports.repositories.jam_repository import JamRepositoryPort
lazy from app.application.ports.repositories.track_repository import TrackRepositoryPort
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort
lazy from app.domain.models.jam import JamQueueItem


@dataclass(slots=True, frozen=True)
class GetJamStateUseCase:
    """Returns room state, currently playing track, and ordered queue."""

    jam_repo: JamRepositoryPort
    user_repo: UserRepositoryPort
    track_repo: TrackRepositoryPort

    def execute(self, jam_id: int, user_id: int) -> JamStateResult:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        jam = self.jam_repo.find_by_id(jam_id)
        if not jam:
            raise EntityNotFoundError(f"Jam session {jam_id} not found.")

        raw_queue = self.jam_repo.list_queue(jam_id)
        current_track_domain = None
        if jam.current_track_id:
            current_track_domain = self.track_repo.find_by_id(jam.current_track_id)

        queue_items: list[JamQueueItem] = []
        for item in raw_queue:
            track = self.track_repo.find_by_id(item.track_id)
            if not track or track.is_deleted:
                continue
            if not user.is_adult and track.explicit:
                continue
            queue_items.append(item)

        current_track = None
        if (
            current_track_domain
            and not current_track_domain.is_deleted
            and (user.is_adult or not current_track_domain.explicit)
        ):
            current_track = current_track_domain

        return JamStateResult(
            jam=jam,
            current_track=current_track,
            queue=queue_items,
        )
