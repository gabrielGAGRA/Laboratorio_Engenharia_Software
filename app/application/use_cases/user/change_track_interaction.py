"""Use case for changing a track swipe interaction by a Premium user."""

from typing import TYPE_CHECKING

from app.application.dtos.discovery_dtos import InteractionResponse
from app.domain.exceptions import EntityNotFoundError, PermissionDeniedError

if TYPE_CHECKING:
    from app.application.ports.repositories.interaction_repository import (
        InteractionRepositoryPort,
    )
    from app.application.ports.repositories.plan_repository import PlanRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort
    from app.domain.models.interaction import InteractionAction


class ChangeTrackInteractionUseCase:
    """Allows Premium subscribers to revise previous swipe gestures on tracks."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        plan_repo: PlanRepositoryPort,
        interaction_repo: InteractionRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._plan_repo = plan_repo
        self._interaction_repo = interaction_repo

    def execute(
        self, user_id: int, track_id: int, new_action: InteractionAction
    ) -> InteractionResponse:
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        plan = self._plan_repo.find_by_id(user.plan_id)
        if not plan or not plan.is_paid:
            raise PermissionDeniedError("Feature exclusive to Premium subscribers.")

        interaction = self._interaction_repo.find_by_user_and_track(user_id, track_id)
        if not interaction:
            raise EntityNotFoundError("Interaction for this track was not found.")

        interaction.action = new_action
        saved = self._interaction_repo.save(interaction)
        return InteractionResponse.from_domain(saved)
