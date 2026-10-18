"""Use case for deleting a user account."""

from typing import TYPE_CHECKING

from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class DeleteUserAccountUseCase:
    """Deletes a user account and associated personal settings."""

    def __init__(self, user_repo: UserRepositoryPort) -> None:
        self._user_repo = user_repo

    def execute(self, user_id: int) -> bool:
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        return self._user_repo.delete(user_id)
