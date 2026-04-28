from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.shared.domain.security.password_hasher import PasswordHasher
from modules.user_views.application.invalidate_cache.invalidate_user_views_cache import (
    InvalidateUserViewsCache,
)
from modules.users.domain.user_not_found_error import UserNotFoundError
from modules.users.domain.user_repository import UserRepository


class InvalidCurrentPasswordError(Exception): ...


class PasswordChanger:
    def __init__(
        self,
        user_repo: UserRepository,
        hasher: PasswordHasher,
        cache_invalidator: InvalidateUserViewsCache,
    ) -> None:
        self._user_repo = user_repo
        self._hasher = hasher
        self._cache_invalidator = cache_invalidator

    def run(self, user_id: str, current_password: str, new_password: str) -> None:
        user = self._user_repo.find_by_id(IdValueObject(user_id))
        if user is None:
            raise UserNotFoundError(user_id)

        if not user.is_active.value:
            raise PermissionError("Account is disabled")

        if not user.password.matches(current_password, self._hasher):
            raise InvalidCurrentPasswordError("Current password is incorrect")

        if current_password == new_password:
            raise ValueError("New password must differ from the current one")

        user.change_password(new_password, self._hasher)
        self._user_repo.save(user)
        self._cache_invalidator.invalidate_all()
