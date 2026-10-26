"""Data transfer objects for administrative use cases."""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateSubscriptionPlanInput:
    plan_id: int
    new_price: float | None = None
    new_name: str | None = None
    max_profiles: int | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class UserPlanSummaryResponse:
    user_id: int | None
    email: str
    display_name: str
    age: int
    plan_name: str
    is_admin: bool


@dataclass(slots=True, frozen=True, kw_only=True)
class ExecutiveDashboardResponse:
    total_users: int
    estimated_net_revenue: float
    users_by_plan: dict[str, int]
    revenue_by_plan: dict[str, float]


@dataclass(slots=True, frozen=True, kw_only=True)
class AudienceReportResponse:
    total_users: int
    total_tracks: int
    active_tracks: int


@dataclass(slots=True, frozen=True, kw_only=True)
class AuditLogEntryResponse:
    event: str
    status: str
