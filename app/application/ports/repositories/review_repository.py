"""Persistence port for reviews and comments."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from app.domain.models import ReviewComment


@runtime_checkable
class ReviewRepositoryPort(Protocol):
    def find_by_id(self, review_id: int) -> ReviewComment | None: ...

    def save(self, review: ReviewComment) -> ReviewComment: ...

    def list_by_track(self, track_id: int, limit: int) -> list[ReviewComment]:
        """Returns non-deleted reviews for a track."""
        ...

    def list_top_recent(self, days: int, limit: int) -> list[ReviewComment]:
        """Returns the most liked non-deleted reviews from the last `days` days."""
        ...
