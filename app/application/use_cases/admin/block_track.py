"""Use case for administrative blocking/soft-deleting of a track."""

from typing import TYPE_CHECKING

from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.track_repository import TrackRepositoryPort


class BlockTrackUseCase:
    """Applies soft-delete to an offensive or deactivated music track."""

    def __init__(self, track_repo: TrackRepositoryPort) -> None:
        self._track_repo = track_repo

    def execute(self, track_id: int) -> bool:
        track = self._track_repo.find_by_id(track_id)
        if not track:
            raise EntityNotFoundError(f"Track {track_id} not found.")

        track.mark_as_deleted()
        self._track_repo.save(track)
        return True
