"""Unit tests for UpdateSubscriptionPlanUseCase."""

from unittest.mock import MagicMock

import pytest

from app.application.commands.admin_commands import UpdateSubscriptionPlanCommand
from app.application.ports.repositories.plan_repository import PlanRepositoryPort
from app.application.use_cases.admin.update_subscription_plan import (
    UpdateSubscriptionPlanUseCase,
)
from app.domain.exceptions import EntityNotFoundError
from app.domain.models.plan import Plan


def test_update_subscription_plan_not_found_raises_error() -> None:
    plan_repo = MagicMock(spec=PlanRepositoryPort)
    plan_repo.find_by_id.return_value = None

    use_case = UpdateSubscriptionPlanUseCase(plan_repo=plan_repo)
    command = UpdateSubscriptionPlanCommand(plan_id=99, new_price=29.90)

    with pytest.raises(EntityNotFoundError, match="Plan 99 not found"):
        use_case.execute(command)

    plan_repo.save.assert_not_called()


def test_update_subscription_plan_updates_all_provided_fields() -> None:
    plan = Plan(
        plan_id=3,
        name="Family",
        initial_monthly_price=34.90,
        initial_max_profiles=4,
    )
    plan_repo = MagicMock(spec=PlanRepositoryPort)
    plan_repo.find_by_id.return_value = plan
    plan_repo.save.side_effect = lambda p: p

    use_case = UpdateSubscriptionPlanUseCase(plan_repo=plan_repo)
    command = UpdateSubscriptionPlanCommand(
        plan_id=3,
        new_price=39.90,
        new_name="Family Plus",
        max_profiles=6,
    )
    updated_plan = use_case.execute(command)

    assert updated_plan.monthly_price == 39.90
    assert updated_plan.name == "Family Plus"
    assert updated_plan.max_profiles == 6
    plan_repo.save.assert_called_once_with(plan)


def test_update_subscription_plan_partial_update_keeps_unmodified_fields() -> None:
    plan = Plan(
        plan_id=2,
        name="Premium",
        initial_monthly_price=19.90,
        initial_max_profiles=1,
    )
    plan_repo = MagicMock(spec=PlanRepositoryPort)
    plan_repo.find_by_id.return_value = plan
    plan_repo.save.side_effect = lambda p: p

    use_case = UpdateSubscriptionPlanUseCase(plan_repo=plan_repo)
    command = UpdateSubscriptionPlanCommand(plan_id=2, new_price=24.90)
    updated_plan = use_case.execute(command)

    assert updated_plan.monthly_price == 24.90
    assert updated_plan.name == "Premium"
    assert updated_plan.max_profiles == 1
    plan_repo.save.assert_called_once_with(plan)


def test_update_subscription_plan_invalid_price_raises_value_error() -> None:
    plan = Plan(
        plan_id=2,
        name="Premium",
        initial_monthly_price=19.90,
        initial_max_profiles=1,
    )
    plan_repo = MagicMock(spec=PlanRepositoryPort)
    plan_repo.find_by_id.return_value = plan

    use_case = UpdateSubscriptionPlanUseCase(plan_repo=plan_repo)
    command = UpdateSubscriptionPlanCommand(plan_id=2, new_price=-5.0)

    with pytest.raises(ValueError, match="Monthly price cannot be negative"):
        use_case.execute(command)

    plan_repo.save.assert_not_called()
