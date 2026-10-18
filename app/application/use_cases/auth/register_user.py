"""Use case for registering a new platform user."""

from dataclasses import dataclass

from app.domain.exceptions import DuplicateEntityError, EntityNotFoundError
lazy from app.application.commands.auth_commands import RegisterUserCommand
lazy from app.application.ports.repositories.plan_repository import PlanRepositoryPort
lazy from app.application.ports.repositories.user_repository import UserRepositoryPort
lazy from app.application.ports.services.password_hasher import PasswordHasherPort
lazy from app.domain.models.plan import Plan
lazy from app.domain.models.user import User


@dataclass(slots=True, frozen=True)
class RegisterUserUseCase:
    """Coordinates registration of a new user account."""

    user_repo: UserRepositoryPort
    plan_repo: PlanRepositoryPort
    password_hasher: PasswordHasherPort

    def execute(self, command: RegisterUserCommand) -> User:
        existing = self.user_repo.find_by_email(command.email)
        if existing:
            raise DuplicateEntityError(f"Email {command.email} is already in use.")

        plan_id = command.plan_id
        if plan_id is None:
            free_plan = self.plan_repo.find_by_name(Plan.DEFAULT_FREE_PLAN_NAME)
            if not free_plan or free_plan.plan_id is None:
                raise EntityNotFoundError("Default Free plan not found.")
            plan_id = free_plan.plan_id
        else:
            plan = self.plan_repo.find_by_id(plan_id)
            if not plan:
                raise EntityNotFoundError(f"Plan with ID {plan_id} not found.")

        hashed_password = self.password_hasher.hash_password(command.password)
        new_user = User(
            user_id=None,
            email=command.email.strip().lower(),
            password_hash=hashed_password,
            display_name=command.display_name.strip(),
            age=command.age,
            plan_id=plan_id,
            is_admin=False,
        )
        return self.user_repo.save(new_user)
