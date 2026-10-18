"""Use case for upvoting or adding a track to a Jam queue."""

from dataclasses import dataclass

from app.domain.exceptions import BusinessRuleViolationError, EntityNotFoundError
from app.domain.models.jam import JamQueueItem
lazy from app.application.commands.jam_commands import VoteJamTrackCommand
lazy from app.application.ports.repositories.jam_repository import JamRepositoryPort
lazy from app.application.ports.repositories.track_repository import TrackRepositoryPort
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort


@dataclass(slots=True, frozen=True)
class VoteJamTrackUseCase:
    """Adds a track or increments vote points in the Jam queue."""

    jam_repo: JamRepositoryPort
    user_repo: UserRepositoryPort
    track_repo: TrackRepositoryPort

    def execute(self, command: VoteJamTrackCommand) -> JamQueueItem:
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

        existing_item = self.jam_repo.find_queue_item(command.jam_id, command.track_id)
        if existing_item is not None:
            existing_item.vote(command.points)
            return self.jam_repo.save_queue_item(existing_item)

        new_item = JamQueueItem(
            jam_id=command.jam_id,
            track_id=command.track_id,
            initial_vote_points=command.points,
        )
        return self.jam_repo.save_queue_item(new_item)
