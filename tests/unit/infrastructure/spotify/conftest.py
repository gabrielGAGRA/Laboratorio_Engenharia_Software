"""Shared fixtures for Spotify adapter tests."""

import pytest

from app.infrastructure.adapters.spotify.auth import SpotifyAuth
from app.infrastructure.adapters.spotify.config import SpotifyCredentials
from app.infrastructure.adapters.spotify.http import SpotifyHttpClient
from tests.utils.fakes import FakeResponse, FakeSession
from tests.utils.payloads import ALL_SCOPES


@pytest.fixture
def make_http():
    """Builds a user-token http client whose API calls replay ``responses``."""

    def build(*responses: FakeResponse) -> tuple[SpotifyHttpClient, FakeSession]:
        token = FakeResponse(
            200, {"access_token": "AT", "expires_in": 3600, "scope": ALL_SCOPES}
        )
        session = FakeSession(token, *responses)
        creds = SpotifyCredentials(
            client_id="id",
            client_secret="s",
            redirect_uri="http://127.0.0.1:8888/cb",
            refresh_token="RT",
        )
        return SpotifyHttpClient(
            SpotifyAuth(creds, session), session, sleep=lambda _: None
        ), session

    return build
