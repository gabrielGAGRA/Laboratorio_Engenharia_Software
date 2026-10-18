"""Use case for administrative blocking/soft-deleting of a track."""

from dataclasses import dataclass

from app.domain.exceptions import EntityNotFoundError
lazy from app.application.ports.repositories.track_repository import TrackRepositoryPort


@dataclass(slots=True, frozen=True)
class BlockTrackUseCase:
    """Applies soft-delete to an offensive or deactivated music track."""

    track_repo: TrackRepositoryPort

    def execute(self, track_id: int) -> bool:
        track = self.track_repo.find_by_id(track_id)
        if not track:
            raise EntityNotFoundError(f"Track {track_id} not found.")

        track.mark_as_deleted()
        self.track_repo.save(track)
        return True
