"""User repository implementation conforming to UserRepositoryPort."""

from app.infrastructure.adapters.sqlite.repositories.user_repository import (
    SQLiteUserRepository,
)

UserRepository = SQLiteUserRepository

__all__ = ["SQLiteUserRepository", "UserRepository"]
