"""Unit tests for SpotifyHttpClient."""

import pytest

from app.domain.exceptions import (
    ExternalServiceError,
    SpotifyError,
    SpotifyForbiddenError,
    SpotifyQuotaExceededError,
)
from app.infrastructure.adapters.spotify.auth import SpotifyAuth
from app.infrastructure.adapters.spotify.config import SpotifyCredentials
from app.infrastructure.adapters.spotify.http import SpotifyHttpClient
from tests.utils.fakes import FakeResponse, FakeSession, network_error

TOKEN = FakeResponse(200, {"access_token": "AT", "expires_in": 3600})


def _client(
    *api_responses: FakeResponse | Exception, sleeps: list[float] | None = None
):
    session = FakeSession(TOKEN, *api_responses)
    auth = SpotifyAuth(SpotifyCredentials(client_id="id", client_secret="s"), session)
    waits = sleeps if sleeps is not None else []
    return SpotifyHttpClient(auth, session, sleep=waits.append), session


@pytest.mark.unit
class TestRequest:
    def test_sends_bearer_and_drops_none_params(self) -> None:
        client, session = _client(FakeResponse(200, {"ok": True}))

        result = client.request("GET", "/search", params={"q": "x", "market": None})

        assert result == {"ok": True}
        call = session.calls[1]
        assert call["url"] == "https://api.spotify.com/v1/search"
        assert call["headers"]["Authorization"] == "Bearer AT"
        assert call["params"] == {"q": "x"}

    def test_204_returns_none(self) -> None:
        client, _ = _client(FakeResponse(204))
        assert client.request("GET", "/me/player") is None

    def test_raw_body_overrides_json_content_type(self) -> None:
        client, session = _client(FakeResponse(202))

        client.request(
            "PUT", "/playlists/p/images", data="B64", content_type="image/jpeg"
        )

        call = session.calls[1]
        assert call["data"] == "B64"
        assert call["headers"]["Content-Type"] == "image/jpeg"

    def test_scope_checked_before_http(self) -> None:
        client, session = _client()
        with pytest.raises(SpotifyForbiddenError):
            client.request("GET", "/me", scopes=frozenset({"user-read-private"}))
        assert all("api.spotify.com" not in call["url"] for call in session.calls)

    def test_403_raises_forbidden_without_retry(self) -> None:
        client, session = _client(FakeResponse(403, {"error": {"message": "nope"}}))
        with pytest.raises(SpotifyForbiddenError):
            client.request("GET", "/x")
        assert len(session.calls) == 2

    def test_other_error_status_raises_spotify_error(self) -> None:
        client, _ = _client(FakeResponse(500, {"error": {"message": "down"}}))
        with pytest.raises(SpotifyError, match="500") as info:
            client.request("GET", "/x")
        assert info.value.details["status_code"] == 500

    def test_network_failure_is_mapped(self) -> None:
        client, _ = _client(network_error())
        with pytest.raises(ExternalServiceError) as info:
            client.request("GET", "/x")
        assert info.value.service_name == "Spotify"


@pytest.mark.unit
class TestRateLimit:
    def test_retries_after_header_then_succeeds(self) -> None:
        sleeps: list[float] = []
        client, session = _client(
            FakeResponse(429, {}, {"Retry-After": "7"}),
            FakeResponse(200, {"ok": 1}),
            sleeps=sleeps,
        )

        assert client.request("GET", "/x") == {"ok": 1}
        assert sleeps == [7]
        assert len(session.calls) == 3

    def test_gives_up_after_max_retries(self) -> None:
        limited = FakeResponse(429, {}, {"Retry-After": "1"})
        client, _ = _client(limited, limited, limited, limited)
        with pytest.raises(SpotifyError, match="rate limit"):
            client.request("GET", "/x")

    def test_quota_exceeded_is_fatal_immediately(self) -> None:
        sleeps: list[float] = []
        body = {"error": {"status": 429, "reason": "QUOTA_EXCEEDED"}}
        client, session = _client(FakeResponse(429, body), sleeps=sleeps)

        with pytest.raises(SpotifyQuotaExceededError):
            client.request("GET", "/x")

        assert sleeps == []
        assert len(session.calls) == 2
