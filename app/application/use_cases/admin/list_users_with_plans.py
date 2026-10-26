"""Use case for listing users and their assigned subscription plans."""

from typing import TYPE_CHECKING

from app.application.dtos.admin_dtos import UserPlanSummaryResponse

if TYPE_CHECKING:
    from app.application.ports.repositories.plan_repository import PlanRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class ListUsersWithPlansUseCase:
    """Lists users alongside their active plan names for administrative management."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        plan_repo: PlanRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._plan_repo = plan_repo

    def execute(self) -> list[UserPlanSummaryResponse]:
        users = self._user_repo.list_all()
        plans = {
            p.plan_id: p.name
            for p in self._plan_repo.list_all()
            if p.plan_id is not None
        }

        return [
            UserPlanSummaryResponse(
                user_id=u.user_id,
                email=u.email,
                display_name=u.display_name,
                age=u.age,
                plan_name=plans.get(u.plan_id, "Unknown"),
                is_admin=u.is_admin,
            )
            for u in users
        ]
