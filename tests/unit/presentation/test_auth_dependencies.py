"""Unit tests for user authentication dependencies."""

from unittest.mock import MagicMock

import pytest

from app.domain.exceptions import AuthenticationRequiredError
from app.domain.models import User
from app.presentation.dependencies.auth import get_current_user_id, require_user


def test_get_current_user_id_bearer_token() -> None:
    user_id = get_current_user_id(authorization="Bearer 42")
    assert user_id == 42


def test_get_current_user_id_raw_authorization_header() -> None:
    user_id = get_current_user_id(authorization="100")
    assert user_id == 100


def test_get_current_user_id_x_user_id_header() -> None:
    user_id = get_current_user_id(x_user_id="77")
    assert user_id == 77


def test_get_current_user_id_query_param_fallback() -> None:
    user_id = get_current_user_id(user_id="88")
    assert user_id == 88


def test_get_current_user_id_precedence() -> None:
    # Authorization header should precede X-User-Id and query param
    assert (
        get_current_user_id(authorization="Bearer 1", x_user_id="2", user_id="3") == 1
    )
    # X-User-Id should precede query param
    assert get_current_user_id(x_user_id="2", user_id="3") == 2


def test_get_current_user_id_missing_all_raises_error() -> None:
    with pytest.raises(AuthenticationRequiredError, match="Authentication required"):
        get_current_user_id()


def test_get_current_user_id_invalid_int_raises_error() -> None:
    with pytest.raises(AuthenticationRequiredError, match="Invalid user ID"):
        get_current_user_id(authorization="Bearer not_a_number")

    with pytest.raises(AuthenticationRequiredError, match="Invalid user ID"):
        get_current_user_id(x_user_id="invalid")

    with pytest.raises(AuthenticationRequiredError, match="Invalid user ID"):
        get_current_user_id(user_id="bad_id")


def test_require_user_success() -> None:
    user = User(
        user_id=10,
        email="user@test.com",
        password_hash="pw",
        display_name="User",
        age=25,
        plan_id=1,
    )
    request = MagicMock()
    request.app.state.container.user_repo.find_by_id.return_value = user

    result = require_user(request=request, user_id=10)
    assert result == 10
    request.app.state.container.user_repo.find_by_id.assert_called_once_with(10)


def test_require_user_not_found_raises_error() -> None:
    request = MagicMock()
    request.app.state.container.user_repo.find_by_id.return_value = None

    with pytest.raises(AuthenticationRequiredError, match="User not found"):
        require_user(request=request, user_id=999)
