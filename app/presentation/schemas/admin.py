"""Administrative presentation schemas."""

from pydantic import BaseModel, ConfigDict, Field


class PlanResponse(BaseModel):
    """Public representation of a subscription plan."""

    model_config = ConfigDict(from_attributes=True)

    plan_id: int
    name: str
    monthly_price: float
    max_profiles: int


class UpdatePlanAdminRequest(BaseModel):
    """Payload for modifying an existing subscription plan tier."""

    new_price: float | None = None
    new_name: str | None = None
    max_profiles: int | None = None


class UpdateTrackExplicitRequest(BaseModel):
    """Payload to alter a track explicit advisory status."""

    explicit: bool


class TrackBlockResponse(BaseModel):
    """Response returned upon blocking a catalog track."""

    model_config = ConfigDict(from_attributes=True)

    blocked: bool


class TrackExplicitResponse(BaseModel):
    """Response returned upon updating explicit status on a track."""

    model_config = ConfigDict(from_attributes=True)

    track_id: int
    explicit: bool


class ExecutiveDashboardResponse(BaseModel):
    """Aggregated platform performance and subscription revenue metrics."""

    model_config = ConfigDict(from_attributes=True)

    total_users: int
    estimated_net_revenue: float
    users_by_plan: dict[str, int] = Field(default_factory=dict)
    revenue_by_plan: dict[str, float] = Field(default_factory=dict)


class AudienceReportResponse(BaseModel):
    """Aggregate volume counts of registered users and catalog tracks."""

    model_config = ConfigDict(from_attributes=True)

    total_users: int
    total_tracks: int
    active_tracks: int


class UserPlanSummaryResponse(BaseModel):
    """Summary overview of a registered user and their assigned subscription plan."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int | None = None
    email: str
    display_name: str
    age: int
    plan_name: str
    is_admin: bool


__all__ = [
    "AudienceReportResponse",
    "ExecutiveDashboardResponse",
    "PlanResponse",
    "TrackBlockResponse",
    "TrackExplicitResponse",
    "UpdatePlanAdminRequest",
    "UpdateTrackExplicitRequest",
    "UserPlanSummaryResponse",
]
