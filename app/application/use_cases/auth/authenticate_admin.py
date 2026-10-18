"""Use case for authenticating administrative user access."""

from dataclasses import dataclass

from app.domain.exceptions import AuthenticationRequiredError, PermissionDeniedError
lazy from app.application.commands.auth_commands import AuthenticateAdminCommand
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort
lazy from app.application.ports.services.password_hasher import PasswordHasherPort
lazy from app.domain.models.user import User


@dataclass(slots=True, frozen=True)
class AuthenticateAdminUseCase:
    """Verifies administrator credentials and privileges."""

    user_repo: UserRepositoryPort
    password_hasher: PasswordHasherPort

    def execute(self, command: AuthenticateAdminCommand) -> User:
        user = self.user_repo.find_by_email(command.email.strip().lower())
        if not user:
            raise AuthenticationRequiredError("Invalid credentials.")

        if not self.password_hasher.verify_password(
            command.password, user.password_hash
        ):
            raise AuthenticationRequiredError("Invalid credentials.")

        if not user.is_admin:
            raise PermissionDeniedError("Access restricted to administrators.")

        return user
