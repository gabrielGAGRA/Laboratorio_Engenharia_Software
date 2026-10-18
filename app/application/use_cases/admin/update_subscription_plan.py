"""Use case for updating subscription plan prices and parameters."""

from dataclasses import dataclass

from app.domain.exceptions import EntityNotFoundError
lazy from app.application.commands.admin_commands import (
    UpdateSubscriptionPlanCommand,
)
lazy from app.application.ports.repositories.plan_repository import PlanRepositoryPort
lazy from app.domain.models.plan import Plan


@dataclass(slots=True, frozen=True)
class UpdateSubscriptionPlanUseCase:
    """Modifies pricing, names, or profile quotas on existing plans."""

    plan_repo: PlanRepositoryPort

    def execute(self, command: UpdateSubscriptionPlanCommand) -> Plan:
        plan = self.plan_repo.find_by_id(command.plan_id)
        if not plan:
            raise EntityNotFoundError(f"Plan {command.plan_id} not found.")

        if command.new_price is not None:
            plan.update_price(command.new_price)

        if command.new_name is not None:
            plan.update_name(command.new_name)

        if command.max_profiles is not None:
            plan.update_max_profiles(command.max_profiles)

        return self.plan_repo.save(plan)
