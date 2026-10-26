"""Persistence port for users."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from app.domain.models import User


@runtime_checkable
class UserRepositoryPort(Protocol):
    def find_by_id(self, user_id: int) -> User | None: ...

    def find_by_email(self, email: str) -> User | None: ...

    def save(self, user: User) -> User: ...

    def delete(self, user_id: int) -> bool: ...

    def list_dependents(self, primary_account_id: int) -> list[User]: ...

    def list_all(self) -> list[User]: ...
