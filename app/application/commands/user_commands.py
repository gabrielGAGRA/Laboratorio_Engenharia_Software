"""Inbound application commands for user profile management."""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateProfileCommand:
    user_id: int
    display_name: str | None = None
    new_password: str | None = None
