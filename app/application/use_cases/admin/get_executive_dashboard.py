"""Use case for calculating executive metrics and financial dashboard."""

from typing import TYPE_CHECKING

from app.application.dtos.admin_dtos import ExecutiveDashboardResponse

if TYPE_CHECKING:
    from app.application.ports.repositories.plan_repository import PlanRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class GetExecutiveDashboardUseCase:
    """Calculates financial metrics and subscriber distribution."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        plan_repo: PlanRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._plan_repo = plan_repo

    def execute(self) -> ExecutiveDashboardResponse:
        users = self._user_repo.list_all()
        plans = self._plan_repo.list_all()
        plan_map = {p.plan_id: p for p in plans if p.plan_id is not None}

        total_revenue = 0.0
        users_by_plan: dict[str, int] = {p.name: 0 for p in plans}
        revenue_by_plan: dict[str, float] = {p.name: 0.0 for p in plans}

        for user in users:
            plan = plan_map.get(user.plan_id)
            if plan:
                users_by_plan[plan.name] = users_by_plan.get(plan.name, 0) + 1
                if user.primary_account_id is None:
                    total_revenue += plan.monthly_price
                    revenue_by_plan[plan.name] = (
                        revenue_by_plan.get(plan.name, 0.0) + plan.monthly_price
                    )

        return ExecutiveDashboardResponse(
            total_users=len(users),
            estimated_net_revenue=round(total_revenue, 2),
            users_by_plan=users_by_plan,
            revenue_by_plan={k: round(v, 2) for k, v in revenue_by_plan.items()},
        )
