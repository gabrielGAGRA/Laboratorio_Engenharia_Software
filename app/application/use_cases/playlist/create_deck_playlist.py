"""Use case for creating a contextual track deck playlist."""

from typing import TYPE_CHECKING

from app.application.dtos.playlist_dtos import (
    CreateDeckPlaylistInput,
    PlaylistResponse,
)
from app.domain.exceptions import EntityNotFoundError
from app.domain.models.playlist import Playlist

if TYPE_CHECKING:
    from app.application.ports.repositories.playlist_repository import (
        PlaylistRepositoryPort,
    )
    from app.application.ports.repositories.track_repository import TrackRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort
    from app.domain.models.track import Track


class CreateDeckPlaylistUseCase:
    """Builds and persists a new playlist matching duration and filter constraints."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        track_repo: TrackRepositoryPort,
        playlist_repo: PlaylistRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._track_repo = track_repo
        self._playlist_repo = playlist_repo

    def execute(self, input_dto: CreateDeckPlaylistInput) -> PlaylistResponse:
        user = self._user_repo.find_by_id(input_dto.user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {input_dto.user_id} not found.")

        candidates = self._track_repo.find_by_filters(
            artist=input_dto.artist,
            genre=input_dto.genre,
            year=input_dto.year,
        )

        if not user.is_adult:
            candidates = [t for t in candidates if not t.explicit]

        if not candidates:
            candidates = self._track_repo.list_active(
                block_explicit=not user.is_adult,
                limit=10,
            )

        selected_tracks: list[Track] = []
        target_seconds = (
            (input_dto.duration_minutes * 60) if input_dto.duration_minutes else None
        )
        accumulated_seconds = 0

        for track in candidates:
            if target_seconds and accumulated_seconds + track.duration_seconds > (
                target_seconds + 60
            ):
                break
            selected_tracks.append(track)
            accumulated_seconds += track.duration_seconds

        playlist = Playlist(
            playlist_id=None,
            user_id=input_dto.user_id,
            name=input_dto.name.strip(),
            description=input_dto.description.strip()
            if input_dto.description
            else None,
            is_exported=False,
            initial_tracks=selected_tracks,
        )
        saved = self._playlist_repo.save(playlist)
        return PlaylistResponse.from_domain(saved)
