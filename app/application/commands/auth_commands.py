"""Inbound application commands for authentication."""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class RegisterUserCommand:
    email: str
    password: str
    display_name: str
    age: int
    plan_id: int | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class AuthenticateUserCommand:
    email: str
    password: str


@dataclass(slots=True, frozen=True, kw_only=True)
class AuthenticateAdminCommand:
    email: str
    password: str
