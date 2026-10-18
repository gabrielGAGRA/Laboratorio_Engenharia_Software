"""Projection results for users and profiles."""

from dataclasses import dataclass

lazy from app.domain.models.plan import Plan
lazy from app.domain.models.user import User


@dataclass(slots=True, frozen=True, kw_only=True)
class UserProfileResult:
    user: User
    plan: Plan


@dataclass(slots=True, frozen=True, kw_only=True)
class AnnualStatsResult:
    user_id: int
    estimated_listening_hours: float
    total_likes: int
    top_genres: list[str]
    top_artists: list[str]
