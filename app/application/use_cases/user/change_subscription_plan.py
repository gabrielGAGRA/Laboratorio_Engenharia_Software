"""Use case for changing a user's subscription plan."""

from dataclasses import dataclass

from app.domain.exceptions import EntityNotFoundError
lazy from app.application.ports.repositories.plan_repository import PlanRepositoryPort
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort
lazy from app.domain.models.user import User


@dataclass(slots=True, frozen=True)
class ChangeSubscriptionPlanUseCase:
    """Changes the subscription plan associated with a user."""

    user_repo: UserRepositoryPort
    plan_repo: PlanRepositoryPort

    def execute(self, user_id: int, new_plan_id: int) -> User:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        new_plan = self.plan_repo.find_by_id(new_plan_id)
        if not new_plan:
            raise EntityNotFoundError(f"Plan with ID {new_plan_id} not found.")

        user.change_plan(new_plan_id)
        return self.user_repo.save(user)
