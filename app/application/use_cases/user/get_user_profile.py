"""Use case for retrieving user profile and active subscription plan."""

from dataclasses import dataclass

from app.application.dtos.user_dtos import UserProfileResult
from app.domain.exceptions import EntityNotFoundError
lazy from app.application.ports.repositories.plan_repository import PlanRepositoryPort
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort


@dataclass(slots=True, frozen=True)
class GetUserProfileUseCase:
    """Retrieves full profile details for a given user alongside their plan."""

    user_repo: UserRepositoryPort
    plan_repo: PlanRepositoryPort

    def execute(self, user_id: int) -> UserProfileResult:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        plan = self.plan_repo.find_by_id(user.plan_id)
        if not plan:
            raise EntityNotFoundError(f"Plan with ID {user.plan_id} not found.")

        return UserProfileResult(
            user=user,
            plan=plan,
        )
