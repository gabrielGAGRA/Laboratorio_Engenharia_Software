"""Domain exception hierarchy."""

from collections.abc import Mapping
from typing import Any


class CustomError(Exception):
    """Root of all project errors; carries no transport semantics."""

    def __init__(
        self,
        message: str,
        *,
        name: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.name = name or type(self).__name__
        self.details = dict(details or {})


class ExternalServiceError(CustomError):
    """An external provider failed or answered unexpectedly."""

    def __init__(
        self,
        message: str,
        *,
        service_name: str,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message, details=details)
        self.service_name = service_name


class SpotifyError(ExternalServiceError):
    """Spotify request failed or answered with an unexpected payload."""

    def __init__(
        self, message: str, *, details: Mapping[str, Any] | None = None
    ) -> None:
        super().__init__(message, service_name="Spotify", details=details)


class SpotifyAuthError(SpotifyError):
    """Spotify credentials or tokens are missing, expired, or revoked."""


class SpotifyForbiddenError(SpotifyError):
    """Spotify denied access: missing scope, user outside the allowlist, or no Premium."""


class SpotifyQuotaExceededError(SpotifyError):
    """Development-mode quota is exhausted; retrying will not help."""


__all__ = [
    "CustomError",
    "ExternalServiceError",
    "SpotifyAuthError",
    "SpotifyError",
    "SpotifyForbiddenError",
    "SpotifyQuotaExceededError",
]
