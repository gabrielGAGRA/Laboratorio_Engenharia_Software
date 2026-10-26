"""Persistence port for tracks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Sequence

    from app.domain.models import Track
    from app.domain.types import TrackId


@runtime_checkable
class TrackRepositoryPort(Protocol):
    def find_by_id(self, track_id: TrackId | int) -> Track | None: ...

    def save(self, track: Track) -> Track: ...

    def list_active(
        self,
        *,
        limit: int,
        excluded_genres: Sequence[str] = (),
        block_explicit: bool = False,
        excluded_ids: Sequence[int] = (),
    ) -> list[Track]:
        """Returns non-deleted tracks eligible for discovery, in a stable order."""
        ...

    def find_by_filters(
        self,
        *,
        artist: str | None = None,
        album: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        query: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Track]: ...

    def count_all(self) -> int: ...
