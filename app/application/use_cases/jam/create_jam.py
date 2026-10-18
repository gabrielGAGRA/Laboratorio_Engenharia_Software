"""Use case for creating a collaborative Jam session."""

from dataclasses import dataclass

from app.domain.exceptions import EntityNotFoundError
from app.domain.models.jam import Jam
lazy from app.application.commands.jam_commands import CreateJamCommand
lazy from app.application.ports.repositories.jam_repository import JamRepositoryPort
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort


@dataclass(slots=True, frozen=True)
class CreateJamUseCase:
    """Creates a new collaborative Jam session with a unique room code."""

    jam_repo: JamRepositoryPort
    user_repo: UserRepositoryPort

    def execute(self, command: CreateJamCommand) -> Jam:
        host = self.user_repo.find_by_id(command.host_user_id)
        if not host:
            raise EntityNotFoundError(f"Host user {command.host_user_id} not found.")

        jam = Jam.create(
            host_user_id=command.host_user_id,
            room_name=command.room_name.strip(),
        )
        return self.jam_repo.save(jam)
