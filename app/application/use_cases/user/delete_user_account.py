"""Use case for deleting a user account."""

from dataclasses import dataclass

from app.domain.exceptions import EntityNotFoundError
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort


@dataclass(slots=True, frozen=True)
class DeleteUserAccountUseCase:
    """Deletes a user account and associated personal settings."""

    user_repo: UserRepositoryPort

    def execute(self, user_id: int) -> bool:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        return self.user_repo.delete(user_id)
