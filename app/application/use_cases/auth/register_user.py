"""Use case for registering a new platform user."""

from typing import TYPE_CHECKING

from app.application.dtos.user_dtos import UserResponse
from app.domain.exceptions import DuplicateEntityError, EntityNotFoundError
from app.domain.models.user import User

if TYPE_CHECKING:
    from app.application.dtos.auth_dtos import RegisterUserInput
    from app.application.ports.repositories.plan_repository import PlanRepositoryPort
    from app.application.ports.repositories.user_repository import UserRepositoryPort
    from app.application.ports.services.password_hasher import PasswordHasherPort


class RegisterUserUseCase:
    """Coordinates registration of a new user account."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        plan_repo: PlanRepositoryPort,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self._user_repo = user_repo
        self._plan_repo = plan_repo
        self._password_hasher = password_hasher

    def execute(self, input_dto: RegisterUserInput) -> UserResponse:
        existing = self._user_repo.find_by_email(input_dto.email)
        if existing:
            raise DuplicateEntityError(f"Email {input_dto.email} is already in use.")

        plan_id = input_dto.plan_id
        if plan_id is None:
            free_plan = self._plan_repo.find_by_name("Free")
            if not free_plan or free_plan.plan_id is None:
                raise EntityNotFoundError("Default Free plan not found.")
            plan_id = free_plan.plan_id
        else:
            plan = self._plan_repo.find_by_id(plan_id)
            if not plan:
                raise EntityNotFoundError(f"Plan with ID {plan_id} not found.")

        hashed_password = self._password_hasher.hash_password(input_dto.password)
        new_user = User(
            user_id=None,
            email=input_dto.email.strip().lower(),
            password_hash=hashed_password,
            display_name=input_dto.display_name.strip(),
            age=input_dto.age,
            plan_id=plan_id,
            is_admin=False,
        )
        saved = self._user_repo.save(new_user)
        return UserResponse.from_domain(saved)
