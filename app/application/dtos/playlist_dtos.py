"""Projection results for playlists."""

from dataclasses import dataclass

lazy from app.domain.models.playlist import Playlist
lazy from app.domain.models.track import Track


@dataclass(slots=True, frozen=True, kw_only=True)
class PlaylistWithTracksResult:
    playlist: Playlist
    tracks: list[Track]
