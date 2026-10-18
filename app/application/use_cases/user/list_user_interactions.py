"""Use case for listing user interaction history."""

from typing import TYPE_CHECKING

from app.application.dtos.discovery_dtos import InteractionResponse
from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.interaction_repository import (
        InteractionRepositoryPort,
    )
    from app.application.ports.repositories.user_repository import UserRepositoryPort
    from app.domain.models.interaction import InteractionAction


class ListUserInteractionsUseCase:
    """Retrieves interaction history for a user, optionally filtered by action."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        interaction_repo: InteractionRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._interaction_repo = interaction_repo

    def execute(
        self, user_id: int, action: InteractionAction | None = None
    ) -> list[InteractionResponse]:
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        interactions = self._interaction_repo.list_by_user(user_id, action=action)
        return [InteractionResponse.from_domain(i) for i in interactions]
