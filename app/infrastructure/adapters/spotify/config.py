"""Spotify Development-mode constants and credentials model."""

from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, field_validator

API_BASE_URL = "https://api.spotify.com/v1"
AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"  # noqa: S105

HTTP_TIMEOUT_SECONDS = 5.0
MAX_RATE_LIMIT_RETRIES = 3
DEFAULT_RETRY_AFTER_SECONDS = 1
TOKEN_EXPIRY_MARGIN_SECONDS = 30

SEARCH_MAX_LIMIT = 10
LIBRARY_URI_BATCH_MAX = 40


class SpotifyCredentials(BaseModel):
    model_config = ConfigDict(frozen=True)

    client_id: str
    client_secret: str | None = None
    redirect_uri: str | None = None
    refresh_token: str | None = None

    @field_validator("redirect_uri")
    @classmethod
    def _require_https_or_loopback_ip(cls, value: str | None) -> str | None:
        if value is None:
            return value
        parsed = urlparse(value)
        is_loopback_ip = parsed.scheme == "http" and parsed.hostname == "127.0.0.1"
        if parsed.scheme != "https" and not is_loopback_ip:
            raise ValueError(
                "redirect_uri must use https or http://127.0.0.1:PORT, not localhost"
            )
        return value
