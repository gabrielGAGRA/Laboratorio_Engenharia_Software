"""Plan repository implementation conforming to PlanRepositoryPort."""

from app.infrastructure.adapters.sqlite.repositories.plan_repository import (
    SQLitePlanRepository,
)

PlanRepository = SQLitePlanRepository

__all__ = ["PlanRepository", "SQLitePlanRepository"]
