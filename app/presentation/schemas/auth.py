"""Authentication and user account presentation schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserResponse(BaseModel):
    """Public representation of an authenticated user profile."""

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
    """Payload for registering a new user."""

    email: str
    password: str = Field(min_length=6)
    display_name: str = Field(min_length=2, max_length=50)
    age: int = Field(ge=0)
    plan_id: int | None = None


class LoginRequest(BaseModel):
    """Credentials payload for user authentication."""

    email: str
    password: str


__all__ = [
    "LoginRequest",
    "RegisterUserRequest",
    "UserResponse",
]
