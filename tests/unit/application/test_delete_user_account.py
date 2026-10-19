"""Unit tests for DeleteUserAccountUseCase."""

from unittest.mock import MagicMock

import pytest

from app.application.ports.repositories.user_repository import UserRepositoryPort
from app.application.use_cases.user.delete_user_account import DeleteUserAccountUseCase
from app.domain.exceptions import EntityNotFoundError
from app.domain.models.user import User


def test_delete_user_account_not_found_raises_error() -> None:
    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = None

    use_case = DeleteUserAccountUseCase(user_repo=user_repo)

    with pytest.raises(EntityNotFoundError, match="User with ID 42 not found"):
        use_case.execute(user_id=42)

    user_repo.delete.assert_not_called()


def test_delete_user_account_deletes_and_returns_true() -> None:
    user = User(
        user_id=42,
        email="bye@test.com",
        password_hash="hash",
        display_name="Bye",
        age=25,
        plan_id=1,
    )
    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = user
    user_repo.delete.return_value = True

    use_case = DeleteUserAccountUseCase(user_repo=user_repo)
    result = use_case.execute(user_id=42)

    assert result is True
    user_repo.find_by_id.assert_called_once_with(42)
    user_repo.delete.assert_called_once_with(42)
