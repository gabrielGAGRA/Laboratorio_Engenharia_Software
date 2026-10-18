"""Projection results for administrative use cases."""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class UserPlanSummaryResult:
    user_id: int | None
    email: str
    display_name: str
    age: int
    plan_name: str
    is_admin: bool


@dataclass(slots=True, frozen=True, kw_only=True)
class ExecutiveDashboardResult:
    total_users: int
    estimated_net_revenue: float
    users_by_plan: dict[str, int]
    revenue_by_plan: dict[str, float]


@dataclass(slots=True, frozen=True, kw_only=True)
class AudienceReportResult:
    total_users: int
    total_tracks: int
    active_tracks: int


@dataclass(slots=True, frozen=True, kw_only=True)
class AuditLogEntryResult:
    event: str
    status: str
