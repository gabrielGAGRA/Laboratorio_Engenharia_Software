"""Use case for downvoting/skipping a track in a Jam queue."""

from dataclasses import dataclass

from app.domain.exceptions import BusinessRuleViolationError, EntityNotFoundError
lazy from app.application.commands.jam_commands import VoteSkipJamTrackCommand
lazy from app.application.ports.repositories.jam_repository import JamRepositoryPort
lazy from app.application.ports.repositories.track_repository import TrackRepositoryPort
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort
lazy from app.domain.models.jam import JamQueueItem


@dataclass(slots=True, frozen=True)
class VoteSkipJamTrackUseCase:
    """Decrements vote points on a queued Jam track."""

    jam_repo: JamRepositoryPort
    user_repo: UserRepositoryPort
    track_repo: TrackRepositoryPort

    def execute(self, command: VoteSkipJamTrackCommand) -> JamQueueItem:
        user = self.user_repo.find_by_id(command.user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {command.user_id} not found.")

        jam = self.jam_repo.find_by_id(command.jam_id)
        if not jam or not jam.is_active:
            raise EntityNotFoundError("Jam room not found or inactive.")

        track = self.track_repo.find_by_id(command.track_id)
        if not track or track.is_deleted:
            raise EntityNotFoundError("Track not found or inactive.")

        if not user.can_listen(track):
            raise BusinessRuleViolationError(
                "Track is blocked for underage users or violates genre preferences."
            )

        item = self.jam_repo.find_queue_item(command.jam_id, command.track_id)
        if not item:
            raise EntityNotFoundError("Track is not currently in the jam queue.")

        item.vote(-1)
        return self.jam_repo.save_queue_item(item)
