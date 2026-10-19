"""Unit tests for CancelSubscriptionPlanUseCase."""

from unittest.mock import MagicMock

import pytest

from app.application.ports.repositories.plan_repository import PlanRepositoryPort
from app.application.ports.repositories.user_repository import UserRepositoryPort
from app.application.use_cases.user.cancel_subscription_plan import (
    CancelSubscriptionPlanUseCase,
)
from app.domain.exceptions import EntityNotFoundError
from app.domain.models.plan import Plan
from app.domain.models.user import User


def test_cancel_subscription_plan_user_not_found_raises_error() -> None:
    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = None
    plan_repo = MagicMock(spec=PlanRepositoryPort)

    use_case = CancelSubscriptionPlanUseCase(user_repo=user_repo, plan_repo=plan_repo)

    with pytest.raises(EntityNotFoundError, match="User with ID 1 not found"):
        use_case.execute(user_id=1)

    user_repo.save.assert_not_called()


def test_cancel_subscription_plan_free_plan_missing_raises_error() -> None:
    user = User(
        user_id=1,
        email="prem@test.com",
        password_hash="hash",
        display_name="Prem",
        age=25,
        plan_id=2,
    )
    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = user
    plan_repo = MagicMock(spec=PlanRepositoryPort)
    plan_repo.find_by_name.return_value = None

    use_case = CancelSubscriptionPlanUseCase(user_repo=user_repo, plan_repo=plan_repo)

    with pytest.raises(EntityNotFoundError, match="Default Free plan not found"):
        use_case.execute(user_id=1)

    user_repo.save.assert_not_called()


def test_cancel_subscription_plan_free_plan_without_id_raises_error() -> None:
    user = User(
        user_id=1,
        email="prem@test.com",
        password_hash="hash",
        display_name="Prem",
        age=25,
        plan_id=2,
    )
    unpersisted_free_plan = Plan(
        plan_id=None,
        name=Plan.DEFAULT_FREE_PLAN_NAME,
        initial_monthly_price=0.0,
    )
    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = user
    plan_repo = MagicMock(spec=PlanRepositoryPort)
    plan_repo.find_by_name.return_value = unpersisted_free_plan

    use_case = CancelSubscriptionPlanUseCase(user_repo=user_repo, plan_repo=plan_repo)

    with pytest.raises(EntityNotFoundError, match="Default Free plan not found"):
        use_case.execute(user_id=1)

    user_repo.save.assert_not_called()


def test_cancel_subscription_plan_reverts_user_to_free_plan() -> None:
    user = User(
        user_id=1,
        email="prem@test.com",
        password_hash="hash",
        display_name="Prem",
        age=25,
        plan_id=2,
    )
    free_plan = Plan(
        plan_id=1,
        name=Plan.DEFAULT_FREE_PLAN_NAME,
        initial_monthly_price=0.0,
    )
    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = user
    user_repo.save.side_effect = lambda u: u
    plan_repo = MagicMock(spec=PlanRepositoryPort)
    plan_repo.find_by_name.return_value = free_plan

    use_case = CancelSubscriptionPlanUseCase(user_repo=user_repo, plan_repo=plan_repo)
    updated_user = use_case.execute(user_id=1)

    assert updated_user.plan_id == 1
    plan_repo.find_by_name.assert_called_once_with(Plan.DEFAULT_FREE_PLAN_NAME)
    user_repo.save.assert_called_once_with(user)
