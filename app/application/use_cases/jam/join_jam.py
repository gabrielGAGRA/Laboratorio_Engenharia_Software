"""Use case for joining an existing Jam session via room code."""

from typing import TYPE_CHECKING

from app.application.dtos.jam_dtos import JamResponse
from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.jam_repository import JamRepositoryPort


class JoinJamUseCase:
    """Finds an active Jam session by its unique invitation room code."""

    def __init__(self, jam_repo: JamRepositoryPort) -> None:
        self._jam_repo = jam_repo

    def execute(self, room_code: str) -> JamResponse:
        jam = self._jam_repo.find_by_code(room_code.strip().upper())
        if not jam or not jam.is_active:
            raise EntityNotFoundError("Jam room not found or inactive.")

        return JamResponse.from_domain(jam)
