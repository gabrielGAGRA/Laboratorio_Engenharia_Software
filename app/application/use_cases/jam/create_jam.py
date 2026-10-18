"""Use case for creating a collaborative Jam session."""

from typing import TYPE_CHECKING

from app.application.dtos.jam_dtos import CreateJamInput, JamResponse
from app.domain.exceptions import EntityNotFoundError
from app.domain.models.jam import Jam

if TYPE_CHECKING:
    from app.application.ports.repositories.jam_repository import JamRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class CreateJamUseCase:
    """Creates a new collaborative Jam session with a unique room code."""

    def __init__(
        self,
        jam_repo: JamRepositoryPort,
        user_repo: UserRepositoryPort,
    ) -> None:
        self._jam_repo = jam_repo
        self._user_repo = user_repo

    def execute(self, input_dto: CreateJamInput) -> JamResponse:
        host = self._user_repo.find_by_id(input_dto.host_user_id)
        if not host:
            raise EntityNotFoundError(f"Host user {input_dto.host_user_id} not found.")

        jam = Jam.create(
            host_user_id=input_dto.host_user_id,
            room_name=input_dto.room_name.strip(),
        )
        saved = self._jam_repo.save(jam)
        return JamResponse.from_domain(saved)
