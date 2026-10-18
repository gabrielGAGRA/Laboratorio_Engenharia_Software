"""Authentication and authorization dependency providers."""

from typing import Annotated

from fastapi import Depends, Header, Query, Request

from app.domain.exceptions import (
    AuthenticationRequiredError,
    PermissionDeniedError,
)

ADMIN_ID_HEADER = "X-Admin-User-Id"
USER_ID_HEADER = "X-User-Id"


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


def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None,
    x_user_id: Annotated[str | None, Header(alias=USER_ID_HEADER)] = None,
    user_id: Annotated[str | None, Query()] = None,
) -> int:
    """Extracts and validates current user identifier from headers or query parameters."""
    raw_val: str | None = None
    if authorization is not None and authorization.strip():
        parts = authorization.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            raw_val = parts[1]
        elif len(parts) == 1:
            raw_val = parts[0]
        else:
            raw_val = authorization.strip()
    elif x_user_id is not None and x_user_id.strip():
        raw_val = x_user_id.strip()
    elif user_id is not None and user_id.strip():
        raw_val = user_id.strip()

    if raw_val is None:
        raise AuthenticationRequiredError("Authentication required.")

    try:
        return int(raw_val)
    except ValueError as exc:
        raise AuthenticationRequiredError("Invalid user ID.") from exc


def require_user(
    request: Request,
    user_id: Annotated[int, Depends(get_current_user_id)],
) -> int:
    """Enforces user credential existence and validation."""
    user = request.app.state.container.user_repo.find_by_id(user_id)
    if not user:
        raise AuthenticationRequiredError("User not found.")
    return user_id


__all__ = [
    "ADMIN_ID_HEADER",
    "USER_ID_HEADER",
    "get_admin_id",
    "get_current_user_id",
    "require_admin",
    "require_user",
]
