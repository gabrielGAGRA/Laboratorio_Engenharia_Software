"""Data transfer objects for track discovery and swipes."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from app.domain.models.interaction import Interaction, InteractionAction


@dataclass(slots=True, frozen=True, kw_only=True)
class RecordSwipeInput:
    user_id: int
    track_id: int
    action: InteractionAction


@dataclass(slots=True, frozen=True, kw_only=True)
class InteractionResponse:
    interaction_id: int | None
    user_id: int
    track_id: int
    action: InteractionAction
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, interaction: Interaction) -> InteractionResponse:
        return cls(
            interaction_id=interaction.interaction_id,
            user_id=interaction.user_id,
            track_id=interaction.track_id,
            action=interaction.action,
            created_at=interaction.created_at,
        )
