"""Use case for associating a Spotify account ID with a user."""

from typing import TYPE_CHECKING

from app.application.dtos.user_dtos import UserResponse
from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class LinkSpotifyAccountUseCase:
    """Links an external Spotify identifier to the user record."""

    def __init__(self, user_repo: UserRepositoryPort) -> None:
        self._user_repo = user_repo

    def execute(self, user_id: int, spotify_id: str) -> UserResponse:
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        user.spotify_id = spotify_id.strip()
        saved = self._user_repo.save(user)
        return UserResponse.from_domain(saved)
