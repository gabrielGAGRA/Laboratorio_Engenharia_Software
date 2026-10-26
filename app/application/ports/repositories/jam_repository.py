"""Persistence port for Jam sessions and their voting queues."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from app.domain.models import Jam, JamQueueItem


@runtime_checkable
class JamRepositoryPort(Protocol):
    def find_by_id(self, jam_id: int) -> Jam | None: ...

    def find_by_code(self, room_code: str) -> Jam | None:
        """Returns the active jam with this room code, if any."""
        ...

    def save(self, jam: Jam) -> Jam: ...

    def find_queue_item(self, jam_id: int, track_id: int) -> JamQueueItem | None: ...

    def save_queue_item(self, item: JamQueueItem) -> JamQueueItem:
        """Persists vote totals computed by `JamQueueItem.vote`."""
        ...

    def list_queue(self, jam_id: int) -> list[JamQueueItem]:
        """Returns the queue ordered by vote points, then insertion time."""
        ...

    def remove_track_from_queue(self, jam_id: int, track_id: int) -> bool: ...
