"""Unit tests for the Spotify client factory."""

import pytest

from app.infrastructure.adapters.spotify.config import SpotifyCredentials
from app.infrastructure.adapters.spotify.factory import build_spotify_client
from tests.utils.fakes import FakeSession

REDIRECT = "http://127.0.0.1:8888/cb"


@pytest.mark.unit
class TestFactory:
    def test_client_credentials_exposes_only_auth_and_catalog(self) -> None:
        client = build_spotify_client(
            SpotifyCredentials(client_id="id", client_secret="s"), FakeSession()
        )
        assert client.catalog is not None
        assert (client.playlists, client.player) == (None, None)

    @pytest.mark.parametrize(
        "credentials",
        [
            SpotifyCredentials(
                client_id="id", client_secret="s", redirect_uri=REDIRECT
            ),
            SpotifyCredentials(client_id="id", redirect_uri=REDIRECT),
        ],
    )
    def test_user_flows_expose_all_modules(
        self, credentials: SpotifyCredentials
    ) -> None:
        client = build_spotify_client(credentials, FakeSession())
        assert client.playlists is not None
        assert client.player is not None
