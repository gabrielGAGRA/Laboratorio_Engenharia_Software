"""Persistence port for playlists."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from app.domain.models import Playlist


@runtime_checkable
class PlaylistRepositoryPort(Protocol):
    def find_by_id(self, playlist_id: int) -> Playlist | None:
        """Returns the playlist aggregate including its tracks."""
        ...

    def list_by_user(self, user_id: int) -> list[Playlist]: ...

    def save(self, playlist: Playlist) -> Playlist:
        """Persists the whole aggregate, including track membership."""
        ...
