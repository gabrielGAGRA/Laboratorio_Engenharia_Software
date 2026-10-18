"""Persistence port for swipe interactions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from app.domain.models import Interaction, InteractionAction


@runtime_checkable
class InteractionRepositoryPort(Protocol):
    def find_by_user_and_track(
        self, user_id: int, track_id: int
    ) -> Interaction | None: ...

    def save(self, interaction: Interaction) -> Interaction: ...

    def list_by_user(
        self, user_id: int, action: InteractionAction | None = None
    ) -> list[Interaction]: ...

    def list_interacted_track_ids(self, user_id: int) -> list[int]: ...
