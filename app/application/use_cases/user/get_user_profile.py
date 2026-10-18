"""Use case for retrieving user profile and active subscription plan."""

from typing import TYPE_CHECKING

from app.application.dtos.plan_dtos import PlanResponse
from app.application.dtos.user_dtos import UserProfileResponse, UserResponse
from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.plan_repository import PlanRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class GetUserProfileUseCase:
    """Retrieves full profile details for a given user alongside their plan."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        plan_repo: PlanRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._plan_repo = plan_repo

    def execute(self, user_id: int) -> UserProfileResponse:
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        plan = self._plan_repo.find_by_id(user.plan_id)
        if not plan:
            raise EntityNotFoundError(f"Plan with ID {user.plan_id} not found.")

        return UserProfileResponse(
            user=UserResponse.from_domain(user),
            plan=PlanResponse.from_domain(plan),
        )
