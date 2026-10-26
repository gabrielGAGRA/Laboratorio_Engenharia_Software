"""Pydantic DTOs for API requests and responses."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plan_id: int
    name: str
    monthly_price: float
    max_profiles: int


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    email: str
    display_name: str
    age: int
    plan_id: int
    spotify_id: str | None = None
    primary_account_id: int | None = None
    blocked_genres: list[str] | frozenset[str] | set[str] | None = None
    is_admin: bool = False
    created_at: datetime | None = None


class RegisterUserRequest(BaseModel):
    email: str
    password: str = Field(min_length=6)
    display_name: str = Field(min_length=2, max_length=50)
    age: int = Field(ge=0)
    plan_id: int | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class UpdateTrackExplicitRequest(BaseModel):
    explicit: bool


class TrackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    track_id: int
    title: str
    artist: str
    duration_seconds: int
    genre: str
    spotify_id: str | None = None
    album: str | None = None
    country: str | None = None
    release_year: int | None = None
    cover_url: str | None = None
    itunes_preview_url: str | None = None
    explicit: bool = False
    is_deleted: bool = False


class InteractionRequest(BaseModel):
    user_id: int
    track_id: int
    action: Literal["like", "superlike", "dislike"]


class InteractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    interaction_id: int
    user_id: int
    track_id: int
    action: str
    created_at: datetime | None = None


class DeckPlaylistRequest(BaseModel):
    user_id: int
    name: str = Field(min_length=1, max_length=100)
    duration_minutes: int | None = Field(default=None, ge=1, le=600)
    genre: str | None = None
    year: int | None = Field(default=None, ge=1900, le=2100)
    artist: str | None = None
    country: str | None = None
    description: str | None = Field(default=None, max_length=500)


class PlaylistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    playlist_id: int
    user_id: int
    name: str
    description: str | None = None
    spotify_playlist_id: str | None = None
    is_exported: bool = False
    tracks: list[TrackResponse] = Field(default_factory=list)


class SwipeAddTrackRequest(BaseModel):
    track_id: int


class UpdateProfileRequest(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=50)
    new_password: str | None = Field(default=None, min_length=6)


class LinkSpotifyRequest(BaseModel):
    user_id: int
    spotify_id: str


class ChangePlanRequest(BaseModel):
    user_id: int
    new_plan_id: int


class ChangeInteractionRequest(BaseModel):
    user_id: int
    track_id: int
    new_action: Literal["like", "superlike", "dislike"]


class BlockedGenresRequest(BaseModel):
    user_id: int
    blocked_genres: str


class AddFamilyMemberRequest(BaseModel):
    primary_account_id: int
    dependent_user_id: int


class CreateJamRequest(BaseModel):
    host_user_id: int
    room_name: str = Field(min_length=1, max_length=100)


class JoinJamRequest(BaseModel):
    room_code: str = Field(min_length=1, max_length=20)


class VoteJamTrackRequest(BaseModel):
    user_id: int
    track_id: int
    points: int = Field(default=1, ge=1, le=10)


class SkipJamTrackRequest(BaseModel):
    user_id: int
    track_id: int


class JamQueueItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    jam_queue_id: int | None = None
    jam_id: int
    track_id: int
    vote_points: int


class JamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    jam_id: int | None = None
    host_user_id: int
    room_name: str
    room_code: str
    is_active: bool
    current_track_id: int | None = None


class JamStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    jam: JamResponse
    current_track: TrackResponse | None = None
    queue: list[JamQueueItemResponse] = Field(default_factory=list)


class PublishReviewRequest(BaseModel):
    user_id: int
    track_id: int
    rating: int = Field(ge=1, le=5)
    text: str | None = Field(default=None, max_length=1000)


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_id: int | None = None
    user_id: int
    track_id: int
    rating: int
    text: str | None = None
    likes_count: int = 0
    is_deleted: bool = False
    created_at: datetime | None = None


class UpdatePlanAdminRequest(BaseModel):
    new_price: float | None = None
    new_name: str | None = None
    max_profiles: int | None = None


class ActionSuccessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    success: bool = True


class TrackBlockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    blocked: bool


class TrackExplicitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    track_id: int
    explicit: bool


class ExecutiveDashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_users: int
    estimated_net_revenue: float
    users_by_plan: dict[str, int] = Field(default_factory=dict)
    revenue_by_plan: dict[str, float] = Field(default_factory=dict)


class AudienceReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_users: int
    total_tracks: int
    active_tracks: int


class UserPlanSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int | None = None
    email: str
    display_name: str
    age: int
    plan_name: str
    is_admin: bool


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: UserResponse
    plan: PlanResponse


class AnnualStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    estimated_listening_hours: float
    total_likes: int
    top_genres: list[str] = Field(default_factory=list)
    top_artists: list[str] = Field(default_factory=list)


class TrackSearchQuery(BaseModel):
    query: str | None = None
    artist: str | None = None
    album: str | None = None
    genre: str | None = None
    year: int | None = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


__all__ = [
    "ActionSuccessResponse",
    "AddFamilyMemberRequest",
    "AnnualStatsResponse",
    "AudienceReportResponse",
    "BlockedGenresRequest",
    "ChangeInteractionRequest",
    "ChangePlanRequest",
    "CreateJamRequest",
    "DeckPlaylistRequest",
    "ExecutiveDashboardResponse",
    "InteractionRequest",
    "InteractionResponse",
    "JamQueueItemResponse",
    "JamResponse",
    "JamStateResponse",
    "JoinJamRequest",
    "LinkSpotifyRequest",
    "LoginRequest",
    "PlanResponse",
    "PlaylistResponse",
    "PublishReviewRequest",
    "RegisterUserRequest",
    "ReviewResponse",
    "SkipJamTrackRequest",
    "SwipeAddTrackRequest",
    "TrackBlockResponse",
    "TrackExplicitResponse",
    "TrackResponse",
    "TrackSearchQuery",
    "UpdatePlanAdminRequest",
    "UpdateProfileRequest",
    "UpdateTrackExplicitRequest",
    "UserProfileResponse",
    "UserPlanSummaryResponse",
    "UserResponse",
    "VoteJamTrackRequest",
]
