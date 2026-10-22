"""Helpers converting Spotify DTOs into persistence import DTOs."""

from app.application.dtos.spotify_dtos import SpotifyTrack, TrackImport

_MS_PER_SECOND = 1000


def to_track_import(track: SpotifyTrack, genre: str) -> TrackImport:
    """``musicas.duracao_segundos`` must be positive, hence the floor of one second."""
    return TrackImport(
        spotify_id=track.spotify_id,
        title=track.title,
        artist=track.artist,
        album=track.album,
        duration_seconds=max(1, round(track.duration_ms / _MS_PER_SECOND)),
        genre=genre,
        cover_url=track.cover_url,
        release_year=track.release_year,
    )
