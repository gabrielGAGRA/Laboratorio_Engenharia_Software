"""Authentication and registration router."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.commands import (
    AuthenticateUserCommand,
    RegisterUserCommand,
)
from app.application.use_cases.auth import (
    AuthenticateUserUseCase,
    RegisterUserUseCase,
)
from app.presentation.dependencies import (
    get_authenticate_user_use_case,
    get_register_user_use_case,
)
from app.presentation.schemas import (
    LoginRequest,
    RegisterUserRequest,
    UserResponse,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    req: RegisterUserRequest,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_user_use_case)],
) -> UserResponse:
    user = use_case.execute(
        RegisterUserCommand(
            email=req.email,
            password=req.password,
            display_name=req.display_name,
            age=req.age,
            plan_id=req.plan_id,
        )
    )
    return UserResponse.model_validate(user)


@router.post("/login", response_model=UserResponse)
def login(
    req: LoginRequest,
    use_case: Annotated[
        AuthenticateUserUseCase, Depends(get_authenticate_user_use_case)
    ],
) -> UserResponse:
    user = use_case.execute(
        AuthenticateUserCommand(email=req.email, password=req.password)
    )
    return UserResponse.model_validate(user)


__all__ = ["router"]
