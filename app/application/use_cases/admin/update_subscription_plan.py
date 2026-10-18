"""Use case for updating subscription plan prices and parameters."""

from typing import TYPE_CHECKING

from app.application.dtos.plan_dtos import PlanResponse
from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.dtos.admin_dtos import UpdateSubscriptionPlanInput
    from app.application.ports.repositories.plan_repository import PlanRepositoryPort


class UpdateSubscriptionPlanUseCase:
    """Modifies pricing, names, or profile quotas on existing plans."""

    def __init__(self, plan_repo: PlanRepositoryPort) -> None:
        self._plan_repo = plan_repo

    def execute(self, input_dto: UpdateSubscriptionPlanInput) -> PlanResponse:
        plan = self._plan_repo.find_by_id(input_dto.plan_id)
        if not plan:
            raise EntityNotFoundError(f"Plan {input_dto.plan_id} not found.")

        if input_dto.new_price is not None:
            plan.update_price(input_dto.new_price)

        if input_dto.new_name is not None:
            plan.name = input_dto.new_name.strip()

        if input_dto.max_profiles is not None:
            plan.update_max_profiles(input_dto.max_profiles)

        saved = self._plan_repo.save(plan)
        return PlanResponse.from_domain(saved)
