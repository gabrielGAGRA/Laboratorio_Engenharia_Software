"""Inbound application commands for collaborative Jam sessions."""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateJamCommand:
    host_user_id: int
    room_name: str


@dataclass(slots=True, frozen=True, kw_only=True)
class VoteJamTrackCommand:
    jam_id: int
    track_id: int
    user_id: int
    points: int = 1


@dataclass(slots=True, frozen=True, kw_only=True)
class VoteSkipJamTrackCommand:
    jam_id: int
    track_id: int
    user_id: int
