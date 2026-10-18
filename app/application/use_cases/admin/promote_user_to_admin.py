"""Use case for promoting a user to administrator status."""

from typing import TYPE_CHECKING

from app.application.dtos.user_dtos import UserResponse
from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class PromoteUserToAdminUseCase:
    """Grants administrator privileges to an existing user."""

    def __init__(self, user_repo: UserRepositoryPort) -> None:
        self._user_repo = user_repo

    def execute(self, user_id: int) -> UserResponse:
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User {user_id} not found.")

        user.is_admin = True
        saved = self._user_repo.save(user)
        return UserResponse.from_domain(saved)
