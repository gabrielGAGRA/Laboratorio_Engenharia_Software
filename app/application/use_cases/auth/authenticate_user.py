"""Use case for authenticating user credentials."""

from typing import TYPE_CHECKING

from app.application.dtos.user_dtos import UserResponse
from app.domain.exceptions import AuthenticationRequiredError

if TYPE_CHECKING:
    from app.application.dtos.auth_dtos import AuthenticateUserInput
    from app.application.ports.repositories.user_repository import UserRepositoryPort
    from app.application.ports.services.password_hasher import PasswordHasherPort


class AuthenticateUserUseCase:
    """Verifies user email and password credentials."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self._user_repo = user_repo
        self._password_hasher = password_hasher

    def execute(self, input_dto: AuthenticateUserInput) -> UserResponse:
        user = self._user_repo.find_by_email(input_dto.email.strip().lower())
        if not user:
            raise AuthenticationRequiredError("Invalid credentials.")

        if not self._password_hasher.verify_password(
            input_dto.password, user.password_hash
        ):
            raise AuthenticationRequiredError("Invalid credentials.")

        return UserResponse.from_domain(user)
