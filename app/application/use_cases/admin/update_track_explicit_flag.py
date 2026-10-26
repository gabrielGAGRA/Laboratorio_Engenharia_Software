"""Use case for toggling the explicit content flag on a track."""

from typing import TYPE_CHECKING

from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.track_repository import TrackRepositoryPort


class UpdateTrackExplicitFlagUseCase:
    """Updates whether a music track is marked as explicit for minors."""

    def __init__(self, track_repo: TrackRepositoryPort) -> None:
        self._track_repo = track_repo

    def execute(self, track_id: int, explicit: bool) -> bool:
        track = self._track_repo.find_by_id(track_id)
        if not track:
            raise EntityNotFoundError(f"Track {track_id} not found.")

        track.explicit = explicit
        self._track_repo.save(track)
        return track.explicit
