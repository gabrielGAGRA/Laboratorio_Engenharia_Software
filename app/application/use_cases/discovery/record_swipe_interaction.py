"""Use case for recording user swipe interactions."""

from typing import TYPE_CHECKING

from app.application.dtos.discovery_dtos import (
    InteractionResponse,
    RecordSwipeInput,
)
from app.domain.exceptions import EntityNotFoundError
from app.domain.models.interaction import Interaction

if TYPE_CHECKING:
    from app.application.ports.repositories.interaction_repository import (
        InteractionRepositoryPort,
    )
    from app.application.ports.repositories.track_repository import TrackRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class RecordSwipeInteractionUseCase:
    """Records user gesture interactions (like, superlike, dislike) on tracks."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        track_repo: TrackRepositoryPort,
        interaction_repo: InteractionRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._track_repo = track_repo
        self._interaction_repo = interaction_repo

    def execute(self, input_dto: RecordSwipeInput) -> InteractionResponse:
        user = self._user_repo.find_by_id(input_dto.user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {input_dto.user_id} not found.")

        track = self._track_repo.find_by_id(input_dto.track_id)
        if not track or track.is_deleted:
            raise EntityNotFoundError(
                f"Track with ID {input_dto.track_id} not found or inactive."
            )

        interaction = Interaction(
            interaction_id=None,
            user_id=input_dto.user_id,
            track_id=input_dto.track_id,
            action=input_dto.action,
        )
        saved = self._interaction_repo.save(interaction)
        return InteractionResponse.from_domain(saved)
