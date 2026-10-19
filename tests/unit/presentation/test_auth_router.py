"""Unit tests for authentication router functions."""

from unittest.mock import MagicMock

from app.application.commands import (
    AuthenticateUserCommand,
    RegisterUserCommand,
)
from app.application.use_cases.auth import (
    AuthenticateUserUseCase,
    RegisterUserUseCase,
)
from app.domain.models import User
from app.presentation.routers.auth import login, register
from app.presentation.schemas import LoginRequest, RegisterUserRequest


def test_register_forwards_command_and_returns_user_response() -> None:
    mock_use_case = MagicMock(spec=RegisterUserUseCase)
    user = User(
        user_id=1,
        email="new@ribbit.com",
        password_hash="hashed_pw",
        display_name="New Frog",
        age=21,
        plan_id=2,
    )
    mock_use_case.execute.return_value = user
    req = RegisterUserRequest(
        email="new@ribbit.com",
        password="secretpassword",
        display_name="New Frog",
        age=21,
        plan_id=2,
    )

    res = register(req=req, use_case=mock_use_case)

    assert res.user_id == 1
    assert res.email == "new@ribbit.com"
    assert res.display_name == "New Frog"
    assert res.age == 21
    assert res.plan_id == 2
    mock_use_case.execute.assert_called_once_with(
        RegisterUserCommand(
            email="new@ribbit.com",
            password="secretpassword",
            display_name="New Frog",
            age=21,
            plan_id=2,
        )
    )


def test_login_forwards_command_and_returns_user_response() -> None:
    mock_use_case = MagicMock(spec=AuthenticateUserUseCase)
    user = User(
        user_id=5,
        email="member@ribbit.com",
        password_hash="hashed_pw",
        display_name="Member",
        age=28,
        plan_id=1,
    )
    mock_use_case.execute.return_value = user
    req = LoginRequest(email="member@ribbit.com", password="mypassword")

    res = login(req=req, use_case=mock_use_case)

    assert res.user_id == 5
    assert res.email == "member@ribbit.com"
    mock_use_case.execute.assert_called_once_with(
        AuthenticateUserCommand(
            email="member@ribbit.com",
            password="mypassword",
        )
    )
