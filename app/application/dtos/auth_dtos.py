"""Data transfer objects for authentication."""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class RegisterUserInput:
    email: str
    password: str
    display_name: str
    age: int
    plan_id: int | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class AuthenticateUserInput:
    email: str
    password: str
