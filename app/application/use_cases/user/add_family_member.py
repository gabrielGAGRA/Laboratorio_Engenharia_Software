"""Use case for adding a dependent member to a family plan."""

from typing import TYPE_CHECKING

from app.application.dtos.user_dtos import UserResponse
from app.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    PermissionDeniedError,
)

if TYPE_CHECKING:
    from app.application.ports.repositories.plan_repository import PlanRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class AddFamilyMemberUseCase:
    """Links a dependent account to a primary Family plan account."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        plan_repo: PlanRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._plan_repo = plan_repo

    def execute(self, primary_user_id: int, dependent_user_id: int) -> UserResponse:
        primary_user = self._user_repo.find_by_id(primary_user_id)
        if not primary_user:
            raise EntityNotFoundError(f"Primary user {primary_user_id} not found.")

        plan = self._plan_repo.find_by_id(primary_user.plan_id)
        if not plan:
            raise EntityNotFoundError(f"Plan with ID {primary_user.plan_id} not found.")

        if not plan.allows_dependents:
            raise PermissionDeniedError(
                "Current plan does not support adding family members."
            )

        if primary_user.primary_account_id is not None:
            raise PermissionDeniedError(
                "A dependent user cannot manage family members."
            )

        if primary_user_id == dependent_user_id:
            raise BusinessRuleViolationError(
                "A user cannot add themselves as a dependent."
            )

        dependent_user = self._user_repo.find_by_id(dependent_user_id)
        if not dependent_user:
            raise EntityNotFoundError(f"Dependent user {dependent_user_id} not found.")

        if dependent_user.primary_account_id == primary_user_id:
            return UserResponse.from_domain(dependent_user)

        if dependent_user.primary_account_id is not None:
            raise BusinessRuleViolationError(
                "This user is already linked to another family account."
            )

        current_dependents = self._user_repo.list_dependents(primary_user_id)
        if not plan.can_accommodate_new_dependent(len(current_dependents)):
            raise BusinessRuleViolationError(
                f"Family plan profile limit of {plan.max_profiles} reached."
            )

        dependent_user.link_primary_account(primary_user_id)
        dependent_user.plan_id = primary_user.plan_id
        saved = self._user_repo.save(dependent_user)
        return UserResponse.from_domain(saved)
