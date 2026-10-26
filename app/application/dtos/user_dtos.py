"""Data transfer objects for users and profiles."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from app.application.dtos.plan_dtos import PlanResponse
    from app.domain.models.user import User


@dataclass(slots=True, frozen=True, kw_only=True)
class UserResponse:
    user_id: int | None
    email: str
    display_name: str
    age: int
    plan_id: int
    is_admin: bool
    spotify_id: str | None = None
    primary_account_id: int | None = None
    blocked_genres: tuple[str, ...] = ()
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, user: User) -> UserResponse:
        return cls(
            user_id=user.user_id,
            email=user.email,
            display_name=user.display_name,
            age=user.age,
            plan_id=user.plan_id,
            is_admin=user.is_admin,
            spotify_id=user.spotify_id,
            primary_account_id=user.primary_account_id,
            blocked_genres=tuple(sorted(user.blocked_genres)),
            created_at=user.created_at,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class UserProfileResponse:
    user: UserResponse
    plan: PlanResponse


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateProfileInput:
    user_id: int
    display_name: str | None = None
    new_password: str | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class AnnualStatsResponse:
    user_id: int
    estimated_listening_hours: float
    total_likes: int
    top_genres: list[str]
    top_artists: list[str]
