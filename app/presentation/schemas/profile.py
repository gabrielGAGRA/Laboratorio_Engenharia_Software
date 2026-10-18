"""User profile and membership presentation schemas."""

from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas.admin import PlanResponse
from app.presentation.schemas.auth import UserResponse


class UpdateProfileRequest(BaseModel):
    """Payload to revise display name or password credentials."""

    display_name: str | None = Field(default=None, min_length=2, max_length=50)
    new_password: str | None = Field(default=None, min_length=6)


class LinkSpotifyRequest(BaseModel):
    """Payload to associate a third-party Spotify identifier."""

    user_id: int
    spotify_id: str


class ChangePlanRequest(BaseModel):
    """Payload to switch subscription plan tier."""

    user_id: int
    new_plan_id: int


class BlockedGenresRequest(BaseModel):
    """Payload to update blocked music genres."""

    user_id: int
    blocked_genres: str | list[str]


class AddFamilyMemberRequest(BaseModel):
    """Payload to link a dependent profile under a primary account."""

    primary_account_id: int
    dependent_user_id: int


class UserProfileResponse(BaseModel):
    """Composite presentation of a user profile along with active plan details."""

    model_config = ConfigDict(from_attributes=True)

    user: UserResponse
    plan: PlanResponse


class AnnualStatsResponse(BaseModel):
    """Aggregated listening statistics and retrospective metrics for a user."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    estimated_listening_hours: float
    total_likes: int
    top_genres: list[str] = Field(default_factory=list)
    top_artists: list[str] = Field(default_factory=list)


__all__ = [
    "AddFamilyMemberRequest",
    "AnnualStatsResponse",
    "BlockedGenresRequest",
    "ChangePlanRequest",
    "LinkSpotifyRequest",
    "UpdateProfileRequest",
    "UserProfileResponse",
]
