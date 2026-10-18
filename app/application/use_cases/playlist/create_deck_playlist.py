"""Use case for creating a contextual track deck playlist."""

from dataclasses import dataclass

from app.domain.exceptions import EntityNotFoundError
from app.domain.models.playlist import Playlist
lazy from app.application.commands.playlist_commands import (
    CreateDeckPlaylistCommand,
)
lazy from app.application.ports.repositories.playlist_repository import (
    PlaylistRepositoryPort,
)
lazy from app.application.ports.repositories.track_repository import TrackRepositoryPort
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort
lazy from app.domain.models.track import Track


@dataclass(slots=True, frozen=True)
class CreateDeckPlaylistUseCase:
    """Builds and persists a new playlist matching duration and filter constraints."""

    user_repo: UserRepositoryPort
    track_repo: TrackRepositoryPort
    playlist_repo: PlaylistRepositoryPort

    def execute(self, command: CreateDeckPlaylistCommand) -> Playlist:
        user = self.user_repo.find_by_id(command.user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {command.user_id} not found.")

        candidates = self.track_repo.find_by_filters(
            artist=command.artist,
            genre=command.genre,
            year=command.year,
        )

        if not user.is_adult:
            candidates = [t for t in candidates if not t.explicit]

        if not candidates:
            candidates = self.track_repo.list_active(
                block_explicit=not user.is_adult,
                limit=10,
            )

        selected_tracks: list[Track] = []
        target_seconds = (
            (command.duration_minutes * 60) if command.duration_minutes else None
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
            user_id=command.user_id,
            name=command.name.strip(),
            description=command.description.strip() if command.description else None,
            is_exported=False,
            initial_tracks=selected_tracks,
        )
        return self.playlist_repo.save(playlist)
