"""Data transfer objects for Jam sessions and queues."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from app.application.dtos.track_dtos import TrackResponse
    from app.domain.models.jam import Jam, JamQueueItem


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateJamInput:
    host_user_id: int
    room_name: str


@dataclass(slots=True, frozen=True, kw_only=True)
class VoteJamTrackInput:
    jam_id: int
    track_id: int
    user_id: int
    points: int = 1


@dataclass(slots=True, frozen=True, kw_only=True)
class VoteSkipJamTrackInput:
    jam_id: int
    track_id: int
    user_id: int


@dataclass(slots=True, frozen=True, kw_only=True)
class JamQueueItemResponse:
    jam_id: int
    track_id: int
    vote_points: int
    jam_queue_id: int | None = None
    added_at: datetime | None = None

    @classmethod
    def from_domain(cls, item: JamQueueItem) -> JamQueueItemResponse:
        return cls(
            jam_queue_id=item.jam_queue_id,
            jam_id=item.jam_id,
            track_id=item.track_id,
            vote_points=item.vote_points,
            added_at=item.added_at,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class JamResponse:
    jam_id: int | None
    host_user_id: int
    room_name: str
    room_code: str
    is_active: bool
    current_track_id: int | None = None
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, jam: Jam) -> JamResponse:
        return cls(
            jam_id=jam.jam_id,
            host_user_id=jam.host_user_id,
            room_name=jam.room_name,
            room_code=jam.room_code,
            is_active=jam.is_active,
            current_track_id=jam.current_track_id,
            created_at=jam.created_at,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class JamStateResponse:
    jam: JamResponse
    current_track: TrackResponse | None
    queue: list[JamQueueItemResponse]
