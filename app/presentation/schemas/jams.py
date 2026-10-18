"""Collaborative Jam session presentation schemas."""

from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas.playlists import TrackResponse


class CreateJamRequest(BaseModel):
    """Payload to initiate a new collaborative Jam session."""

    host_user_id: int
    room_name: str = Field(min_length=1, max_length=100)


class JoinJamRequest(BaseModel):
    """Payload to join an ongoing Jam session via room code."""

    room_code: str = Field(min_length=1, max_length=20)


class VoteJamTrackRequest(BaseModel):
    """Payload to vote points for a track in a Jam queue."""

    user_id: int
    track_id: int
    points: int = Field(default=1, ge=1, le=10)


class SkipJamTrackRequest(BaseModel):
    """Payload to register a skip vote for the active Jam track."""

    user_id: int
    track_id: int


class JamQueueItemResponse(BaseModel):
    """Public representation of an entry in the Jam playback queue."""

    model_config = ConfigDict(from_attributes=True)

    jam_queue_id: int | None = None
    jam_id: int
    track_id: int
    vote_points: int


class JamResponse(BaseModel):
    """Public representation of a Jam session."""

    model_config = ConfigDict(from_attributes=True)

    jam_id: int | None = None
    host_user_id: int
    room_name: str
    room_code: str
    is_active: bool
    current_track_id: int | None = None


class JamStateResponse(BaseModel):
    """Public representation of current Jam playback and queue state."""

    model_config = ConfigDict(from_attributes=True)

    jam: JamResponse
    current_track: TrackResponse | None = None
    queue: list[JamQueueItemResponse] = Field(default_factory=list)


__all__ = [
    "CreateJamRequest",
    "JamQueueItemResponse",
    "JamResponse",
    "JamStateResponse",
    "JoinJamRequest",
    "SkipJamTrackRequest",
    "VoteJamTrackRequest",
]
