"""Use case for exporting a playlist to an external Spotify account."""

from typing import TYPE_CHECKING

from app.application.dtos.playlist_dtos import PlaylistResponse
from app.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    PermissionDeniedError,
)

if TYPE_CHECKING:
    from app.application.ports.repositories.playlist_repository import (
        PlaylistRepositoryPort,
    )
    from app.application.ports.repositories.user_repository import UserRepositoryPort
    from app.application.ports.services.music_service import PlaylistExportPort


class ExportPlaylistToSpotifyUseCase:
    """Exports a user playlist to Spotify using external integration."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        playlist_repo: PlaylistRepositoryPort,
        export_port: PlaylistExportPort,
    ) -> None:
        self._user_repo = user_repo
        self._playlist_repo = playlist_repo
        self._export_port = export_port

    def execute(self, user_id: int, playlist_id: int) -> PlaylistResponse:
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found.")

        if not user.spotify_id:
            raise BusinessRuleViolationError(
                "User does not have a linked Spotify account."
            )

        playlist = self._playlist_repo.find_by_id(playlist_id)
        if not playlist:
            raise EntityNotFoundError(f"Playlist with ID {playlist_id} not found.")

        if playlist.user_id != user_id:
            raise PermissionDeniedError(
                "Access denied: cannot export a playlist that does not belong to you."
            )

        external_track_ids = [t.spotify_id or str(t.track_id) for t in playlist.tracks]
        spotify_playlist_id = self._export_port.export_playlist(
            account_id=user.spotify_id,
            name=playlist.name,
            track_ids=external_track_ids,
        )

        playlist.export(spotify_playlist_id)
        saved = self._playlist_repo.save(playlist)
        return PlaylistResponse.from_domain(saved)
