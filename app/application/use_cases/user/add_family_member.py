"""Use case for adding a dependent member to a family plan."""

from dataclasses import dataclass

from app.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    PermissionDeniedError,
)
lazy from app.application.ports.repositories.plan_repository import PlanRepositoryPort
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort
lazy from app.domain.models.user import User


@dataclass(slots=True, frozen=True)
class AddFamilyMemberUseCase:
    """Links a dependent account to a primary Family plan account."""

    user_repo: UserRepositoryPort
    plan_repo: PlanRepositoryPort

    def execute(self, primary_user_id: int, dependent_user_id: int) -> User:
        primary_user = self.user_repo.find_by_id(primary_user_id)
        if not primary_user:
            raise EntityNotFoundError(f"Primary user {primary_user_id} not found.")

        plan = self.plan_repo.find_by_id(primary_user.plan_id)
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

        dependent_user = self.user_repo.find_by_id(dependent_user_id)
        if not dependent_user:
            raise EntityNotFoundError(f"Dependent user {dependent_user_id} not found.")

        if dependent_user.primary_account_id == primary_user_id:
            return dependent_user

        if dependent_user.primary_account_id is not None:
            raise BusinessRuleViolationError(
                "This user is already linked to another family account."
            )

        current_dependents = self.user_repo.list_dependents(primary_user_id)
        if not plan.can_accommodate_new_dependent(len(current_dependents)):
            raise BusinessRuleViolationError(
                f"Family plan profile limit of {plan.max_profiles} reached."
            )

        dependent_user.link_primary_account(primary_user_id)
        dependent_user.change_plan(primary_user.plan_id)
        return self.user_repo.save(dependent_user)
