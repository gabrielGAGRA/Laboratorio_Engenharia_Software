"""Use case for changing a user's subscription plan."""

from typing import TYPE_CHECKING

from app.application.dtos.user_dtos import UserResponse
from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.plan_repository import PlanRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class ChangeSubscriptionPlanUseCase:
    """Changes the subscription plan associated with a user."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        plan_repo: PlanRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._plan_repo = plan_repo

    def execute(self, user_id: int, new_plan_id: int) -> UserResponse:
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        new_plan = self._plan_repo.find_by_id(new_plan_id)
        if not new_plan:
            raise EntityNotFoundError(f"Plan with ID {new_plan_id} not found.")

        user.plan_id = new_plan_id
        saved = self._user_repo.save(user)
        return UserResponse.from_domain(saved)
