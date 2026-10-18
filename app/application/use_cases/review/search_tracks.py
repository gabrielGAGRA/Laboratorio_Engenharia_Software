"""Use case for filtering and searching track catalog."""

from dataclasses import dataclass

from app.domain.exceptions import EntityNotFoundError
lazy from app.application.commands.review_commands import SearchTracksCommand
lazy from app.application.ports.repositories.track_repository import TrackRepositoryPort
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort
lazy from app.domain.models.track import Track


@dataclass(slots=True, frozen=True)
class SearchTracksUseCase:
    """Searches music tracks by artist, album, genre, release year, or query text."""

    user_repo: UserRepositoryPort
    track_repo: TrackRepositoryPort

    def execute(self, command: SearchTracksCommand) -> list[Track]:
        user = self.user_repo.find_by_id(command.user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {command.user_id} not found.")

        tracks = self.track_repo.find_by_filters(
            artist=command.artist,
            album=command.album,
            genre=command.genre,
            year=command.year,
            query=command.query,
            limit=command.limit,
            offset=command.offset,
        )

        if not user.is_adult:
            tracks = [t for t in tracks if not t.explicit]

        return tracks
