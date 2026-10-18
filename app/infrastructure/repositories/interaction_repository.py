"""Interaction repository implementation conforming to InteractionRepositoryPort."""

from app.infrastructure.adapters.sqlite.repositories.interaction_repository import (
    SQLiteInteractionRepository,
)

InteractionRepository = SQLiteInteractionRepository

__all__ = ["InteractionRepository", "SQLiteInteractionRepository"]
