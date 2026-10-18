"""Inbound application commands for administrative actions."""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateSubscriptionPlanCommand:
    plan_id: int
    new_price: float | None = None
    new_name: str | None = None
    max_profiles: int | None = None
