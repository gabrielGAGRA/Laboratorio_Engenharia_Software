"""Factory exposing only the Spotify modules the credential type allows."""

from typing import NamedTuple

import niquests

from app.infrastructure.adapters.spotify.auth import SpotifyAuth, SpotifyAuthMode
from app.infrastructure.adapters.spotify.catalog import SpotifyCatalog
from app.infrastructure.adapters.spotify.config import SpotifyCredentials
from app.infrastructure.adapters.spotify.http import SpotifyHttpClient
from app.infrastructure.adapters.spotify.player import SpotifyPlayer
from app.infrastructure.adapters.spotify.playlists import SpotifyPlaylists


class SpotifyClient(NamedTuple):
    """``playlists`` and ``player`` are None for client-credentials (no ``/me/*`` access)."""

    auth: SpotifyAuth
    catalog: SpotifyCatalog
    playlists: SpotifyPlaylists | None
    player: SpotifyPlayer | None


def build_spotify_client(
    credentials: SpotifyCredentials, session: niquests.Session | None = None
) -> SpotifyClient:
    http_session = session or niquests.Session()
    auth = SpotifyAuth(credentials, http_session)
    http = SpotifyHttpClient(auth, http_session)
    has_user_modules = auth.mode is not SpotifyAuthMode.CLIENT_CREDENTIALS
    return SpotifyClient(
        auth=auth,
        catalog=SpotifyCatalog(http),
        playlists=SpotifyPlaylists(http) if has_user_modules else None,
        player=SpotifyPlayer(http) if has_user_modules else None,
    )


__all__ = ["SpotifyClient", "build_spotify_client"]
