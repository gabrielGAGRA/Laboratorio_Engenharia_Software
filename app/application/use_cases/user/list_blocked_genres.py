"""Use case for listing user's blocked genres."""

from typing import TYPE_CHECKING

from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class ListBlockedGenresUseCase:
    """Lists all blocked genres configured on a user's profile."""

    def __init__(self, user_repo: UserRepositoryPort) -> None:
        self._user_repo = user_repo

    def execute(self, user_id: int) -> list[str]:
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        return sorted(user.blocked_genres)
