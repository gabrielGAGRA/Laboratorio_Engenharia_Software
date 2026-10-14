"""Domain exception hierarchy. Pure Python, no HTTP or transport semantics."""

from typing import Any


class CustomError(Exception):
    """Root domain exception."""

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
    """Raised when a requested domain entity does not exist."""


class BusinessRuleViolationError(DomainError):
    """Raised when an operation violates a domain invariant or business rule."""


class DuplicateEntityError(DomainError):
    """Raised when attempting to create an entity that already exists."""


class UnauthorizedError(DomainError):
    """Raised when authentication credentials are missing or invalid."""


class ForbiddenError(DomainError):
    """Raised when user permissions or subscription level are insufficient."""
