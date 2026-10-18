"""Inbound application commands for catalog search and reviews."""

from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class SearchTracksCommand:
    user_id: int
    artist: str | None = None
    album: str | None = None
    genre: str | None = None
    year: int | None = None
    query: str | None = None
    limit: int = 50
    offset: int = 0


@dataclass(slots=True, frozen=True, kw_only=True)
class PublishReviewCommand:
    user_id: int
    track_id: int
    rating: int
    text: str | None = None
