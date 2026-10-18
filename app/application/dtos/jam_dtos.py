"""Projection results for Jam sessions and queues."""

from dataclasses import dataclass

lazy from app.domain.models.jam import Jam, JamQueueItem
lazy from app.domain.models.track import Track


@dataclass(slots=True, frozen=True, kw_only=True)
class JamStateResult:
    jam: Jam
    current_track: Track | None
    queue: list[JamQueueItem]
