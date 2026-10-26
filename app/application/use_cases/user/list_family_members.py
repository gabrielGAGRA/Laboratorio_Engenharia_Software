"""Use case for listing dependent family members."""

from typing import TYPE_CHECKING

from app.application.dtos.user_dtos import UserResponse
from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class ListFamilyMembersUseCase:
    """Lists all dependent profiles linked to a primary family account."""

    def __init__(self, user_repo: UserRepositoryPort) -> None:
        self._user_repo = user_repo

    def execute(self, primary_user_id: int) -> list[UserResponse]:
        primary_user = self._user_repo.find_by_id(primary_user_id)
        if not primary_user:
            raise EntityNotFoundError(f"Primary user {primary_user_id} not found.")

        dependents = self._user_repo.list_dependents(primary_user_id)
        return [UserResponse.from_domain(u) for u in dependents]
