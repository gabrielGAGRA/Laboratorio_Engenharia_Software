"""Use case for fetching the next track candidate for swipe discovery."""

from typing import TYPE_CHECKING

from app.application.dtos.track_dtos import TrackResponse
from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.interaction_repository import (
        InteractionRepositoryPort,
    )
    from app.application.ports.repositories.track_repository import TrackRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class GetNextDiscoveryTrackUseCase:
    """Finds the next active track matching user age and genre preferences."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        track_repo: TrackRepositoryPort,
        interaction_repo: InteractionRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._track_repo = track_repo
        self._interaction_repo = interaction_repo

    def execute(self, user_id: int) -> TrackResponse | None:
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        block_explicit = not user.is_adult
        blocked_genres = tuple(user.blocked_genres)
        interacted_ids = self._interaction_repo.list_interacted_track_ids(user_id)

        candidates = self._track_repo.list_active(
            excluded_genres=blocked_genres,
            block_explicit=block_explicit,
            excluded_ids=interacted_ids,
            limit=1,
        )

        return TrackResponse.from_domain(candidates[0]) if candidates else None
