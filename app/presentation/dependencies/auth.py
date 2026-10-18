"""Authentication and authorization dependency providers."""

from typing import Annotated

from fastapi import Depends, Header, Request

from app.domain.exceptions import (
    AuthenticationRequiredError,
    PermissionDeniedError,
)

ADMIN_ID_HEADER = "X-Admin-User-Id"


def get_admin_id(
    header: Annotated[str | None, Header(alias=ADMIN_ID_HEADER)] = None,
) -> int:
    """Extracts and validates that an administrator ID header is present."""
    if header is None:
        raise AuthenticationRequiredError("Administrator ID header missing.")
    try:
        return int(header)
    except ValueError as exc:
        raise AuthenticationRequiredError("Invalid administrator ID header.") from exc


def require_admin(
    request: Request,
    admin_id: Annotated[int, Depends(get_admin_id)],
) -> int:
    """Enforces admin credential existence and role validation."""
    admin_user = request.app.state.container.user_repo.find_by_id(admin_id)
    if not admin_user:
        raise AuthenticationRequiredError("Administrator user not found.")
    if not admin_user.is_admin:
        raise PermissionDeniedError("Access restricted to administrators.")
    return admin_id


__all__ = [
    "ADMIN_ID_HEADER",
    "get_admin_id",
    "require_admin",
]
