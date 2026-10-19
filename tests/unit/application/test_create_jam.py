"""Unit tests for CreateJamUseCase."""

from unittest.mock import MagicMock

import pytest

from app.application.commands.jam_commands import CreateJamCommand
from app.application.ports.repositories.jam_repository import JamRepositoryPort
from app.application.ports.repositories.user_repository import UserRepositoryPort
from app.application.use_cases.jam.create_jam import CreateJamUseCase
from app.domain.exceptions import EntityNotFoundError
from app.domain.models.user import User


def test_create_jam_success_strips_room_name_and_saves_jam() -> None:
    host = User(
        user_id=7,
        email="host@ribbit.com",
        password_hash="pw",
        display_name="DJ Frog",
        age=24,
        plan_id=2,
    )
    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = host

    jam_repo = MagicMock(spec=JamRepositoryPort)
    jam_repo.save.side_effect = lambda j: j

    use_case = CreateJamUseCase(jam_repo=jam_repo, user_repo=user_repo)
    command = CreateJamCommand(host_user_id=7, room_name="  Late Night Pond  ")

    result = use_case.execute(command)

    assert result.host_user_id == 7
    assert result.room_name == "Late Night Pond"
    assert result.is_active is True
    assert result.room_code.startswith("JAM-")
    user_repo.find_by_id.assert_called_once_with(7)
    jam_repo.save.assert_called_once_with(result)


def test_create_jam_host_not_found_raises_entity_not_found() -> None:
    user_repo = MagicMock(spec=UserRepositoryPort)
    user_repo.find_by_id.return_value = None
    jam_repo = MagicMock(spec=JamRepositoryPort)

    use_case = CreateJamUseCase(jam_repo=jam_repo, user_repo=user_repo)
    command = CreateJamCommand(host_user_id=999, room_name="Room")

    with pytest.raises(EntityNotFoundError, match="Host user 999 not found"):
        use_case.execute(command)

    jam_repo.save.assert_not_called()
