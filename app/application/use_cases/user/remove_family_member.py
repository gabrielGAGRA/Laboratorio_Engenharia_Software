"""Use case for removing a dependent member from a family plan."""

from typing import TYPE_CHECKING

from app.application.dtos.user_dtos import UserResponse
from app.domain.exceptions import EntityNotFoundError, PermissionDeniedError

if TYPE_CHECKING:
    from app.application.ports.repositories.plan_repository import PlanRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class RemoveFamilyMemberUseCase:
    """Unlinks a dependent account from a primary account and reverts to Free plan."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        plan_repo: PlanRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._plan_repo = plan_repo

    def execute(self, primary_user_id: int, member_user_id: int) -> UserResponse:
        primary_user = self._user_repo.find_by_id(primary_user_id)
        if not primary_user:
            raise EntityNotFoundError(f"Primary user {primary_user_id} not found.")

        member_user = self._user_repo.find_by_id(member_user_id)
        if not member_user:
            raise EntityNotFoundError(f"Member user {member_user_id} not found.")

        if member_user.primary_account_id != primary_user_id:
            raise PermissionDeniedError(
                "This profile does not belong to your family account."
            )

        free_plan = self._plan_repo.find_by_name("Free")
        if not free_plan or free_plan.plan_id is None:
            raise EntityNotFoundError("Default Free plan not found.")

        member_user.primary_account_id = None
        member_user.plan_id = free_plan.plan_id
        saved = self._user_repo.save(member_user)
        return UserResponse.from_domain(saved)
