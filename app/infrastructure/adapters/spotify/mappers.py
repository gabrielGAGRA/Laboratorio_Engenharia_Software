"""Mappers from Spotify JSON payloads to application DTOs."""

from collections.abc import Iterable, Mapping, Sequence
from typing import Any, TypeGuard

from pydantic import ValidationError

from app.application.dtos.spotify_dtos import (
    SpotifyPlaybackState,
    SpotifyPlaylist,
    SpotifyQueue,
    SpotifyTrack,
)
from app.domain.exceptions import SpotifyError

_YEAR_DIGITS = 4


def drop_none(values: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}


def is_track(data: Any) -> TypeGuard[Mapping[str, Any]]:
    return isinstance(data, dict) and data.get("type", "track") == "track"


def map_track(data: Mapping[str, Any]) -> SpotifyTrack:
    try:
        album: Mapping[str, Any] = data.get("album") or {}
        images: Sequence[Mapping[str, Any]] = album.get("images") or []
        release_date = album.get("release_date") or ""
        year = release_date[:_YEAR_DIGITS]
        return SpotifyTrack(
            spotify_id=data["id"],
            uri=data["uri"],
            title=data["name"],
            artist=", ".join(artist["name"] for artist in data["artists"]),
            album=album.get("name"),
            duration_ms=data["duration_ms"],
            cover_url=images[0]["url"] if images else None,
            preview_url=data.get("preview_url"),
            release_year=int(year) if year.isdigit() else None,
        )
    except (KeyError, TypeError, ValidationError) as exc:
        raise SpotifyError("Spotify returned an unexpected track payload") from exc


def map_tracks(items: Iterable[Any]) -> list[SpotifyTrack]:
    """Maps tracks and silently skips episodes and removed (null) entries."""
    return [map_track(item) for item in items if is_track(item)]


def map_playlist(data: Mapping[str, Any]) -> SpotifyPlaylist:
    try:
        return SpotifyPlaylist(
            spotify_id=data["id"],
            name=data["name"],
            description=data.get("description"),
            public=data.get("public"),
            snapshot_id=data.get("snapshot_id"),
        )
    except (KeyError, TypeError, ValidationError) as exc:
        raise SpotifyError("Spotify returned an unexpected playlist payload") from exc


def map_queue(data: Mapping[str, Any]) -> SpotifyQueue:
    current = data.get("currently_playing")
    return SpotifyQueue(
        currently_playing=map_track(current) if is_track(current) else None,
        queue=tuple(map_tracks(data.get("queue") or [])),
    )


def map_playback_state(data: Mapping[str, Any]) -> SpotifyPlaybackState:
    device: Mapping[str, Any] = data.get("device") or {}
    item = data.get("item")
    try:
        return SpotifyPlaybackState(
            is_playing=data["is_playing"],
            progress_ms=data.get("progress_ms"),
            device_id=device.get("id"),
            device_name=device.get("name"),
            track=map_track(item) if is_track(item) else None,
        )
    except (KeyError, ValidationError) as exc:
        raise SpotifyError("Spotify returned an unexpected playback payload") from exc


def read_snapshot_id(data: Mapping[str, Any] | None) -> str:
    if not data or "snapshot_id" not in data:
        raise SpotifyError("Spotify response did not include a snapshot_id")
    return str(data["snapshot_id"])
