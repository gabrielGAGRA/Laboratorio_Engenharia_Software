"""Use case for filtering and searching track catalog."""

from typing import TYPE_CHECKING

from app.application.dtos.track_dtos import TrackResponse
from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.dtos.review_dtos import SearchTracksInput
    from app.application.ports.repositories.track_repository import TrackRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort


class SearchTracksUseCase:
    """Searches music tracks by artist, album, genre, release year, or query text."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        track_repo: TrackRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._track_repo = track_repo

    def execute(self, input_dto: SearchTracksInput) -> list[TrackResponse]:
        user = self._user_repo.find_by_id(input_dto.user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {input_dto.user_id} not found.")

        tracks = self._track_repo.find_by_filters(
            artist=input_dto.artist,
            album=input_dto.album,
            genre=input_dto.genre,
            year=input_dto.year,
            query=input_dto.query,
            limit=input_dto.limit,
            offset=input_dto.offset,
        )

        if not user.is_adult:
            tracks = [t for t in tracks if not t.explicit]

        return [TrackResponse.from_domain(t) for t in tracks]
