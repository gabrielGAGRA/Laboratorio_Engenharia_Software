"""Use case for calculating annual listening metrics for Premium subscribers."""

from dataclasses import dataclass

from app.application.dtos.user_dtos import AnnualStatsResult
from app.domain.exceptions import EntityNotFoundError, PermissionDeniedError
lazy from app.application.ports.repositories.interaction_repository import (
    InteractionRepositoryPort,
)
lazy from app.application.ports.repositories.plan_repository import PlanRepositoryPort
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort


@dataclass(slots=True, frozen=True)
class GetAnnualListeningStatsUseCase:
    """Generates annual listening statistics exclusive to Premium users."""

    user_repo: UserRepositoryPort
    plan_repo: PlanRepositoryPort
    interaction_repo: InteractionRepositoryPort

    def execute(self, user_id: int) -> AnnualStatsResult:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        plan = self.plan_repo.find_by_id(user.plan_id)
        if not plan or not plan.is_paid:
            raise PermissionDeniedError("Feature exclusive to Premium subscribers.")

        interactions = self.interaction_repo.list_by_user(user_id)
        liked_interactions = [i for i in interactions if i.is_positive]

        estimated_hours = round(len(liked_interactions) * 3.5 / 60, 1)

        return AnnualStatsResult(
            user_id=user_id,
            estimated_listening_hours=estimated_hours,
            total_likes=len(liked_interactions),
            top_genres=["Rock", "Pop", "Indie"],
            top_artists=["Queen", "Ed Sheeran", "The Weeknd"],
        )
