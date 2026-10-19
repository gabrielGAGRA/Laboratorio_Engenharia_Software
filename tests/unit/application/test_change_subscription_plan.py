"""Unit tests for ChangeSubscriptionPlanUseCase."""

from unittest.mock import MagicMock

import pytest

from app.application.ports.repositories.plan_repository import PlanRepositoryPort
from app.application.ports.repositories.user_repository import UserRepositoryPort
from app.application.use_cases.user.change_subscription_plan import (
    ChangeSubscriptionPlanUseCase,
)
from app.domain.exceptions import EntityNotFoundError
from app.domain.models.plan import Plan
from app.domain.models.user import User


def test_change_subscription_plan_user_not_found_raises_error() -> None:
    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = None
    plan_repo = MagicMock(spec=PlanRepositoryPort)

    use_case = ChangeSubscriptionPlanUseCase(user_repo=user_repo, plan_repo=plan_repo)

    with pytest.raises(EntityNotFoundError, match="User with ID 1 not found"):
        use_case.execute(user_id=1, new_plan_id=2)

    user_repo.save.assert_not_called()


def test_change_subscription_plan_target_plan_not_found_raises_error() -> None:
    user = User(
        user_id=1,
        email="user@test.com",
        password_hash="hash",
        display_name="User",
        age=22,
        plan_id=1,
    )
    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = user
    plan_repo = MagicMock(spec=PlanRepositoryPort)
    plan_repo.find_by_id.return_value = None

    use_case = ChangeSubscriptionPlanUseCase(user_repo=user_repo, plan_repo=plan_repo)

    with pytest.raises(EntityNotFoundError, match="Plan with ID 99 not found"):
        use_case.execute(user_id=1, new_plan_id=99)

    user_repo.save.assert_not_called()


def test_change_subscription_plan_updates_and_saves_user() -> None:
    user = User(
        user_id=1,
        email="user@test.com",
        password_hash="hash",
        display_name="User",
        age=22,
        plan_id=1,
    )
    premium_plan = Plan(
        plan_id=2,
        name="Premium",
        initial_monthly_price=19.90,
        initial_max_profiles=1,
    )
    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = user
    user_repo.save.side_effect = lambda u: u
    plan_repo = MagicMock(spec=PlanRepositoryPort)
    plan_repo.find_by_id.return_value = premium_plan

    use_case = ChangeSubscriptionPlanUseCase(user_repo=user_repo, plan_repo=plan_repo)
    updated_user = use_case.execute(user_id=1, new_plan_id=2)

    assert updated_user.plan_id == 2
    plan_repo.find_by_id.assert_called_once_with(2)
    user_repo.save.assert_called_once_with(user)
