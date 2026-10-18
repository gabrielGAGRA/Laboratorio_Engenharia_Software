"""Domain model representing a platform user."""

from dataclasses import dataclass
from typing import ClassVar, Self
from datetime import datetime

from app.domain.models.track import Track


@dataclass(slots=True, kw_only=True, eq=False)
class User:
    MIN_ADULT_AGE: ClassVar[int] = 18

    user_id: int | None = None
    email: str
    password_hash: str
    display_name: str
    age: int
    plan_id: int
    spotify_id: str | None = None
    primary_account_id: int | None = None
    blocked_genres: frozenset[str] = frozenset()
    is_admin: bool = False
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.email.strip():
            raise ValueError("Email cannot be blank.")
        if not self.display_name.strip():
            raise ValueError("Display name cannot be blank.")
        if self.age < 0:
            raise ValueError("Age cannot be negative.")
        self.blocked_genres = frozenset(
            genre.strip().lower() for genre in self.blocked_genres if genre.strip()
        )

    @property
    def is_adult(self) -> bool:
        return self.age >= self.MIN_ADULT_AGE

    def can_listen(self, track: Track) -> bool:
        if not self.is_adult and track.explicit:
            return False
        return track.genre.strip().lower() not in self.blocked_genres

    def link_primary_account(self, primary_account_id: int) -> Self:
        if self.user_id is not None and primary_account_id == self.user_id:
            raise ValueError("Cannot link user account to itself as primary account.")
        self.primary_account_id = primary_account_id
        return self
