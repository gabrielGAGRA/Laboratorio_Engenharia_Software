"""Use case for adding an individual track to a playlist."""

from typing import TYPE_CHECKING

from app.application.dtos.playlist_dtos import (
    AddTrackToPlaylistInput,
    PlaylistResponse,
)
from app.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    PermissionDeniedError,
)

if TYPE_CHECKING:
    from app.application.ports.repositories.playlist_repository import (
        PlaylistRepositoryPort,
    )
    from app.application.ports.repositories.track_repository import TrackRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class AddTrackToPlaylistUseCase:
    """Adds a track to an aggregate playlist after validating ownership and age permissions."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        track_repo: TrackRepositoryPort,
        playlist_repo: PlaylistRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._track_repo = track_repo
        self._playlist_repo = playlist_repo

    def execute(self, input_dto: AddTrackToPlaylistInput) -> PlaylistResponse:
        user = self._user_repo.find_by_id(input_dto.user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {input_dto.user_id} not found.")

        playlist = self._playlist_repo.find_by_id(input_dto.playlist_id)
        if not playlist:
            raise EntityNotFoundError(
                f"Playlist with ID {input_dto.playlist_id} not found."
            )

        if playlist.user_id != input_dto.user_id:
            raise PermissionDeniedError(
                "Access denied: playlist does not belong to this user."
            )

        track = self._track_repo.find_by_id(input_dto.track_id)
        if not track or track.is_deleted:
            raise EntityNotFoundError(
                f"Track with ID {input_dto.track_id} not found or inactive."
            )

        if not user.can_listen(track):
            raise BusinessRuleViolationError(
                "Track is blocked for underage users or violates genre preferences."
            )

        playlist.add_track(track)
        saved = self._playlist_repo.save(playlist)
        return PlaylistResponse.from_domain(saved)
