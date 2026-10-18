"""Use case for canceling a subscription plan and reverting to Free."""

from dataclasses import dataclass

from app.domain.exceptions import EntityNotFoundError
from app.domain.models.plan import Plan
lazy from app.application.ports.repositories.plan_repository import PlanRepositoryPort
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort
lazy from app.domain.models.user import User


@dataclass(slots=True, frozen=True)
class CancelSubscriptionPlanUseCase:
    """Cancels a paid subscription plan, reverting the user account to Free."""

    user_repo: UserRepositoryPort
    plan_repo: PlanRepositoryPort

    def execute(self, user_id: int) -> User:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        free_plan = self.plan_repo.find_by_name(Plan.DEFAULT_FREE_PLAN_NAME)
        if not free_plan or free_plan.plan_id is None:
            raise EntityNotFoundError("Default Free plan not found.")

        user.change_plan(free_plan.plan_id)
        return self.user_repo.save(user)
