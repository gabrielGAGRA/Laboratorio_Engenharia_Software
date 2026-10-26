"""Use case for updating display name or password of a user."""

from typing import TYPE_CHECKING

from app.application.dtos.user_dtos import UpdateProfileInput, UserResponse
from app.domain.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from app.application.ports.repositories.user_repository import UserRepositoryPort
    from app.application.ports.services.password_hasher import PasswordHasherPort


class UpdateProfileUseCase:
    """Updates user profile attributes such as display name and password."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self._user_repo = user_repo
        self._password_hasher = password_hasher

    def execute(self, input_dto: UpdateProfileInput) -> UserResponse:
        user = self._user_repo.find_by_id(input_dto.user_id)
        if not user:
            raise EntityNotFoundError(f"User with ID {input_dto.user_id} not found.")

        if input_dto.display_name:
            user.display_name = input_dto.display_name.strip()

        if input_dto.new_password:
            user.password_hash = self._password_hasher.hash_password(
                input_dto.new_password
            )

        saved = self._user_repo.save(user)
        return UserResponse.from_domain(saved)
