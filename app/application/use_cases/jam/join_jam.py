"""Use case for joining an existing Jam session via room code."""

from dataclasses import dataclass

from app.domain.exceptions import EntityNotFoundError
lazy from app.application.ports.repositories.jam_repository import JamRepositoryPort
lazy from app.domain.models.jam import Jam


@dataclass(slots=True, frozen=True)
class JoinJamUseCase:
    """Finds an active Jam session by its unique invitation room code."""

    jam_repo: JamRepositoryPort

    def execute(self, room_code: str) -> Jam:
        jam = self.jam_repo.find_by_code(room_code.strip().upper())
        if not jam or not jam.is_active:
            raise EntityNotFoundError("Jam room not found or inactive.")

        return jam
