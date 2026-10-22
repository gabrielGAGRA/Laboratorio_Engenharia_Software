"""Spotify Web API adapters."""

from app.infrastructure.adapters.spotify.config import SpotifyCredentials
from app.infrastructure.adapters.spotify.factory import (
    SpotifyClient,
    build_spotify_client,
)

__all__ = ["SpotifyClient", "SpotifyCredentials", "build_spotify_client"]
