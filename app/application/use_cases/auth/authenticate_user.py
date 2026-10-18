"""Use case for authenticating user credentials."""

from dataclasses import dataclass

from app.domain.exceptions import AuthenticationRequiredError
lazy from app.application.commands.auth_commands import AuthenticateUserCommand
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort
lazy from app.application.ports.services.password_hasher import PasswordHasherPort
lazy from app.domain.models.user import User


@dataclass(slots=True, frozen=True)
class AuthenticateUserUseCase:
    """Verifies user email and password credentials."""

    user_repo: UserRepositoryPort
    password_hasher: PasswordHasherPort

    def execute(self, command: AuthenticateUserCommand) -> User:
        user = self.user_repo.find_by_email(command.email.strip().lower())
        if not user:
            raise AuthenticationRequiredError("Invalid credentials.")

        if not self.password_hasher.verify_password(
            command.password, user.password_hash
        ):
            raise AuthenticationRequiredError("Invalid credentials.")

        return user
