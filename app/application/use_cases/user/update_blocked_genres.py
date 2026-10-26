"""Use case for updating blocked genres for Premium users."""

from typing import TYPE_CHECKING

from app.application.dtos.user_dtos import UserResponse
from app.domain.exceptions import EntityNotFoundError, PermissionDeniedError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from app.application.ports.repositories.plan_repository import PlanRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class UpdateBlockedGenresUseCase:
    """Updates blocked music genre filters for a Premium user."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        plan_repo: PlanRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._plan_repo = plan_repo

    def execute(self, user_id: int, blocked_genres: Sequence[str]) -> UserResponse:
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        plan = self._plan_repo.find_by_id(user.plan_id)
        if not plan or not plan.is_paid:
            raise PermissionDeniedError("Feature exclusive to Premium subscribers.")

        user.blocked_genres = frozenset(
            g.strip().lower() for g in blocked_genres if g.strip()
        )
        saved = self._user_repo.save(user)
        return UserResponse.from_domain(saved)
