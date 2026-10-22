"""Unit tests for SpotifyAuth."""

import base64
import hashlib
from urllib.parse import parse_qs, urlparse

import pytest

from app.domain.exceptions import SpotifyAuthError, SpotifyForbiddenError
from app.infrastructure.adapters.spotify.auth import SpotifyAuth, SpotifyAuthMode
from app.infrastructure.adapters.spotify.config import SpotifyCredentials
from tests.utils.fakes import FakeResponse, FakeSession

REDIRECT = "http://127.0.0.1:8888/callback"


def _token(
    access: str = "AT", refresh: str | None = None, scope: str | None = None
) -> FakeResponse:
    body = {"access_token": access, "expires_in": 3600}
    if refresh:
        body["refresh_token"] = refresh
    if scope:
        body["scope"] = scope
    return FakeResponse(200, body)


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


@pytest.mark.unit
class TestMode:
    def test_client_credentials_when_only_secret(self) -> None:
        creds = SpotifyCredentials(client_id="id", client_secret="sec")
        assert (
            SpotifyAuthMode.from_credentials(creds)
            is SpotifyAuthMode.CLIENT_CREDENTIALS
        )

    def test_auth_code_when_secret_and_redirect(self) -> None:
        creds = SpotifyCredentials(
            client_id="id", client_secret="sec", redirect_uri=REDIRECT
        )
        assert SpotifyAuthMode.from_credentials(creds) is SpotifyAuthMode.AUTH_CODE

    def test_auth_code_when_secret_and_refresh_token(self) -> None:
        creds = SpotifyCredentials(
            client_id="id", client_secret="sec", refresh_token="RT"
        )
        assert SpotifyAuthMode.from_credentials(creds) is SpotifyAuthMode.AUTH_CODE

    def test_pkce_when_redirect_without_secret(self) -> None:
        creds = SpotifyCredentials(client_id="id", redirect_uri=REDIRECT)
        assert SpotifyAuthMode.from_credentials(creds) is SpotifyAuthMode.PKCE

    def test_client_id_alone_is_invalid(self) -> None:
        with pytest.raises(ValueError, match="client_secret or redirect_uri"):
            SpotifyAuthMode.from_credentials(SpotifyCredentials(client_id="id"))

    @pytest.mark.parametrize(
        "uri", ["http://localhost:8888/cb", "http://example.com/cb"]
    )
    def test_redirect_uri_must_be_https_or_loopback_ip(self, uri: str) -> None:
        with pytest.raises(ValueError, match="redirect_uri"):
            SpotifyCredentials(client_id="id", client_secret="s", redirect_uri=uri)


@pytest.mark.unit
class TestClientCredentials:
    def test_fetches_token_with_basic_header(self) -> None:
        session = FakeSession(_token("AT1"))
        auth = SpotifyAuth(
            SpotifyCredentials(client_id="id", client_secret="sec"), session
        )

        assert auth.get_access_token() == "AT1"

        call = session.calls[0]
        expected = base64.b64encode(b"id:sec").decode()
        assert call["headers"]["Authorization"] == f"Basic {expected}"
        assert call["data"] == {"grant_type": "client_credentials"}
        assert call["url"] == "https://accounts.spotify.com/api/token"

    def test_cached_until_expiry_then_renewed(self) -> None:
        clock = Clock()
        session = FakeSession(_token("AT1"), _token("AT2"))
        auth = SpotifyAuth(
            SpotifyCredentials(client_id="id", client_secret="sec"),
            session,
            clock=clock,
        )

        assert auth.get_access_token() == "AT1"
        clock.now = 1000
        assert auth.get_access_token() == "AT1"
        clock.now = 3600
        assert auth.get_access_token() == "AT2"
        assert len(session.calls) == 2

    def test_scoped_call_is_forbidden_locally(self) -> None:
        auth = SpotifyAuth(
            SpotifyCredentials(client_id="id", client_secret="sec"), FakeSession()
        )
        with pytest.raises(SpotifyForbiddenError):
            auth.require_any_scope(frozenset({"user-top-read"}))


@pytest.mark.unit
class TestAuthorizationCode:
    def _auth(
        self, *responses: FakeResponse, refresh_token: str | None = None
    ) -> SpotifyAuth:
        creds = SpotifyCredentials(
            client_id="id",
            client_secret="sec",
            redirect_uri=REDIRECT,
            refresh_token=refresh_token,
        )
        return SpotifyAuth(creds, FakeSession(*responses))

    def test_authorize_url_has_expected_params(self) -> None:
        url = self._auth().get_authorize_url(["a", "b"], state="xyz")

        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        assert (
            f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            == "https://accounts.spotify.com/authorize"
        )
        assert query["response_type"] == ["code"]
        assert query["scope"] == ["a b"]
        assert query["state"] == ["xyz"]
        assert query["redirect_uri"] == [REDIRECT]
        assert "code_challenge" not in query

    def test_exchange_code_stores_tokens_and_scopes(self) -> None:
        auth = self._auth(_token("AT", "RT", "user-top-read playlist-read-private"))

        tokens = auth.exchange_code("CODE")

        assert tokens.refresh_token == "RT"
        assert auth.get_access_token() == "AT"
        auth.require_any_scope(frozenset({"user-top-read"}))
        with pytest.raises(SpotifyForbiddenError):
            auth.require_any_scope(frozenset({"user-modify-playback-state"}))

    def test_refresh_replaces_refresh_token_when_returned(self) -> None:
        session = FakeSession(_token("AT2", "RT2"))
        creds = SpotifyCredentials(
            client_id="id",
            client_secret="sec",
            redirect_uri=REDIRECT,
            refresh_token="RT1",
        )
        auth = SpotifyAuth(creds, session)

        assert auth.get_access_token() == "AT2"

        assert session.calls[0]["data"] == {
            "grant_type": "refresh_token",
            "refresh_token": "RT1",
        }
        session.calls.clear()
        session._responses.append(_token("AT3"))  # noqa: SLF001
        auth.refresh_access_token()
        assert session.calls[0]["data"]["refresh_token"] == "RT2"

    def test_without_refresh_token_requires_authorization(self) -> None:
        with pytest.raises(SpotifyAuthError, match="authorization"):
            self._auth().get_access_token()

    def test_invalid_grant_clears_tokens(self) -> None:
        auth = self._auth(
            FakeResponse(400, {"error": "invalid_grant"}), refresh_token="RT1"
        )
        with pytest.raises(SpotifyAuthError, match="invalid_grant"):
            auth.refresh_access_token()
        with pytest.raises(SpotifyAuthError, match="authorization"):
            auth.get_access_token()


@pytest.mark.unit
class TestPkce:
    def test_url_challenge_matches_verifier_sent_on_exchange(self) -> None:
        session = FakeSession(_token("AT", "RT"))
        auth = SpotifyAuth(
            SpotifyCredentials(client_id="id", redirect_uri=REDIRECT), session
        )

        url = auth.get_authorize_url(["a"], state="s")
        auth.exchange_code("CODE")

        query = parse_qs(urlparse(url).query)
        data = session.calls[0]["data"]
        digest = hashlib.sha256(data["code_verifier"].encode()).digest()
        challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
        assert query["code_challenge_method"] == ["S256"]
        assert query["code_challenge"] == [challenge]
        assert data["client_id"] == "id"
        assert "Authorization" not in session.calls[0]["headers"]

    def test_exchange_before_authorize_url_fails(self) -> None:
        auth = SpotifyAuth(
            SpotifyCredentials(client_id="id", redirect_uri=REDIRECT), FakeSession()
        )
        with pytest.raises(SpotifyAuthError, match="code_verifier"):
            auth.exchange_code("CODE")
