"""Persistence port for playlists."""

from typing import Protocol, runtime_checkable

lazy from app.domain.models import Playlist


@runtime_checkable
class PlaylistRepositoryPort(Protocol):
    def find_by_id(self, playlist_id: int) -> Playlist | None:
        """Returns the playlist aggregate including its tracks."""
        ...

    def list_by_user(self, user_id: int) -> list[Playlist]: ...

    def save(self, playlist: Playlist) -> Playlist:
        """Persists the whole aggregate, including track membership."""
        ...
