"""Use case for adding an individual track to a playlist."""

from dataclasses import dataclass

from app.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    PermissionDeniedError,
)
lazy from app.application.commands.playlist_commands import (
    AddTrackToPlaylistCommand,
)
lazy from app.application.ports.repositories.playlist_repository import (
    PlaylistRepositoryPort,
)
lazy from app.application.ports.repositories.track_repository import TrackRepositoryPort
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort
lazy from app.domain.models.playlist import Playlist


@dataclass(slots=True, frozen=True)
class AddTrackToPlaylistUseCase:
    """Adds a track to an aggregate playlist after validating ownership and age permissions."""

    user_repo: UserRepositoryPort
    track_repo: TrackRepositoryPort
    playlist_repo: PlaylistRepositoryPort

    def execute(self, command: AddTrackToPlaylistCommand) -> Playlist:
        user = self.user_repo.find_by_id(command.user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {command.user_id} not found.")

        playlist = self.playlist_repo.find_by_id(command.playlist_id)
        if not playlist:
            raise EntityNotFoundError(
                f"Playlist with ID {command.playlist_id} not found."
            )

        if not playlist.is_owned_by(command.user_id):
            raise PermissionDeniedError(
                "Access denied: playlist does not belong to this user."
            )

        track = self.track_repo.find_by_id(command.track_id)
        if not track or track.is_deleted:
            raise EntityNotFoundError(
                f"Track with ID {command.track_id} not found or inactive."
            )

        if not user.can_listen(track):
            raise BusinessRuleViolationError(
                "Track is blocked for underage users or violates genre preferences."
            )

        playlist.add_track(track)
        return self.playlist_repo.save(playlist)
