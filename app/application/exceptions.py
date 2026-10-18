"""Application errors mapped to HTTP responses by the presentation layer."""

from typing import Any


class CustomError(Exception):
    """Root application exception."""

    def __init__(
        self,
        message: str,
        name: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.name = name or self.__class__.__name__
        self.details = details or {}


class DomainError(CustomError):
    """Base error for business rule failures."""


class EntityNotFoundError(DomainError):
    """Raised when a requested entity does not exist."""


class BusinessRuleViolationError(DomainError):
    """Raised when an operation violates a business rule."""


class DuplicateEntityError(DomainError):
    """Raised when an entity already exists."""


class UnauthorizedError(DomainError):
    """Raised when authentication credentials are missing or invalid."""


class ForbiddenError(DomainError):
    """Raised when the user lacks permission for an operation."""
