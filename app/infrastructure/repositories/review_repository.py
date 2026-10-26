"""Review repository implementation conforming to ReviewRepositoryPort."""

from app.infrastructure.adapters.sqlite.repositories.review_repository import (
    SQLiteReviewRepository,
)

ReviewRepository = SQLiteReviewRepository

__all__ = ["ReviewRepository", "SQLiteReviewRepository"]
