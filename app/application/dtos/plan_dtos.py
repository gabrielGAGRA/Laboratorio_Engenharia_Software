"""Data transfer objects for subscription plans."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.models.plan import Plan


@dataclass(slots=True, frozen=True, kw_only=True)
class PlanResponse:
    plan_id: int | None
    name: str
    monthly_price: float
    max_profiles: int
    is_paid: bool
    allows_dependents: bool

    @classmethod
    def from_domain(cls, plan: Plan) -> PlanResponse:
        return cls(
            plan_id=plan.plan_id,
            name=plan.name,
            monthly_price=plan.monthly_price,
            max_profiles=plan.max_profiles,
            is_paid=plan.is_paid,
            allows_dependents=plan.allows_dependents,
        )
