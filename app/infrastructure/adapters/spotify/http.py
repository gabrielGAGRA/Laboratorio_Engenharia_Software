"""Spotify Web API HTTP client: token injection, 429 handling, and error mapping."""

import time
from collections.abc import Callable, Mapping
from http import HTTPStatus
from typing import Any

import niquests

from app.domain.exceptions import (
    SpotifyError,
    SpotifyForbiddenError,
    SpotifyQuotaExceededError,
)
from app.infrastructure.adapters.spotify.auth import SpotifyAuth
from app.infrastructure.adapters.spotify.config import (
    API_BASE_URL,
    DEFAULT_RETRY_AFTER_SECONDS,
    HTTP_TIMEOUT_SECONDS,
    MAX_RATE_LIMIT_RETRIES,
)


class SpotifyHttpClient:
    def __init__(
        self,
        auth: SpotifyAuth,
        session: niquests.Session,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._auth = auth
        self._session = session
        self._sleep = sleep

    def request(  # noqa: PLR0913
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any = None,
        data: str | None = None,
        content_type: str | None = None,
        scopes: frozenset[str] = frozenset(),
    ) -> Any | None:
        """Calls the API; ``scopes`` means at least one of them must be granted."""
        self._auth.get_access_token()
        self._auth.require_any_scope(scopes)
        kwargs: dict[str, Any] = {"timeout": HTTP_TIMEOUT_SECONDS}
        if params:
            kwargs["params"] = {k: v for k, v in params.items() if v is not None}
        if json is not None:
            kwargs["json"] = json
        if data is not None:
            kwargs["data"] = data
        retries = 0
        while True:
            response = self._send(
                method, path, content_type or "application/json", kwargs
            )
            if response.status_code != HTTPStatus.TOO_MANY_REQUESTS:
                return self._parse(response)
            self._raise_if_quota_exceeded(response)
            if retries >= MAX_RATE_LIMIT_RETRIES:
                raise SpotifyError(
                    "Spotify rate limit persisted after retries", details={"path": path}
                )
            retries += 1
            self._sleep(self._retry_after(response))

    def _send(
        self, method: str, path: str, content_type: str, kwargs: dict[str, Any]
    ) -> niquests.Response:
        headers = {
            "Authorization": f"Bearer {self._auth.get_access_token()}",
            "Content-Type": content_type,
        }
        try:
            return self._session.request(
                method, f"{API_BASE_URL}{path}", headers=headers, **kwargs
            )
        except niquests.RequestException as exc:
            raise SpotifyError(
                f"Failed to communicate with Spotify API: {exc}", details={"path": path}
            ) from exc

    @staticmethod
    def _parse(response: niquests.Response) -> Any | None:
        status = response.status_code or 0
        if status == HTTPStatus.NO_CONTENT:
            return None
        if status >= HTTPStatus.BAD_REQUEST:
            details = {"status_code": status}
            if status == HTTPStatus.FORBIDDEN:
                raise SpotifyForbiddenError(
                    "Spotify denied access: scope missing, user not allowlisted, or no Premium",
                    details=details,
                )
            raise SpotifyError(f"Spotify API returned status {status}", details=details)
        try:
            return response.json()
        except ValueError:
            return None

    @staticmethod
    def _raise_if_quota_exceeded(response: niquests.Response) -> None:
        try:
            error = response.json().get("error")
        except (ValueError, AttributeError):  # fmt: skip
            return
        if isinstance(error, dict) and error.get("reason") == "QUOTA_EXCEEDED":
            raise SpotifyQuotaExceededError("Spotify Development-mode quota exceeded")

    @staticmethod
    def _retry_after(response: niquests.Response) -> float:
        try:
            return float(
                response.headers.get("Retry-After", DEFAULT_RETRY_AFTER_SECONDS)
            )
        except ValueError:
            return DEFAULT_RETRY_AFTER_SECONDS
