"""Use case for listing all available subscription plans."""

from typing import TYPE_CHECKING

from app.application.dtos.plan_dtos import PlanResponse

if TYPE_CHECKING:
    from app.application.ports.repositories.plan_repository import PlanRepositoryPort


class ListPlansUseCase:
    """Lists all active platform subscription plans."""

    def __init__(self, plan_repo: PlanRepositoryPort) -> None:
        self._plan_repo = plan_repo

    def execute(self) -> list[PlanResponse]:
        plans = self._plan_repo.list_all()
        return [PlanResponse.from_domain(p) for p in plans]
