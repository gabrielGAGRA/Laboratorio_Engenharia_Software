"""Use case for canceling a subscription plan and reverting to Free."""

from typing import TYPE_CHECKING

from app.application.dtos.user_dtos import UserResponse
from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.plan_repository import PlanRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class CancelSubscriptionPlanUseCase:
    """Cancels a paid subscription plan, reverting the user account to Free."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        plan_repo: PlanRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._plan_repo = plan_repo

    def execute(self, user_id: int) -> UserResponse:
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        free_plan = self._plan_repo.find_by_name("Free")
        if not free_plan or free_plan.plan_id is None:
            raise EntityNotFoundError("Default Free plan not found.")

        user.plan_id = free_plan.plan_id
        saved = self._user_repo.save(user)
        return UserResponse.from_domain(saved)
