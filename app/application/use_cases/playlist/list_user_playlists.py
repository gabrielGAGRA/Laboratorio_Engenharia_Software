"""Use case for listing all playlists owned by a user."""

from typing import TYPE_CHECKING

from app.application.dtos.playlist_dtos import PlaylistResponse
from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.playlist_repository import (
        PlaylistRepositoryPort,
    )
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class ListUserPlaylistsUseCase:
    """Retrieves all playlists belonging to a specific user."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        playlist_repo: PlaylistRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._playlist_repo = playlist_repo

    def execute(self, user_id: int) -> list[PlaylistResponse]:
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        playlists = self._playlist_repo.list_by_user(user_id)
        return [PlaylistResponse.from_domain(p) for p in playlists]
