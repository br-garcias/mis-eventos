from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.shared.domain.security.password_hasher import PasswordHasher
from modules.user_views.application.invalidate_cache.invalidate_user_views_cache import (
    InvalidateUserViewsCache,
)
from modules.users.domain.user_repository import UserRepository
from modules.users.domain.user_not_found_error import UserNotFoundError
from modules.roles.domain.role_repository import RoleRepository



class UserUpdater:
    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        hasher: PasswordHasher,
        cache_invalidator: InvalidateUserViewsCache,
    ) -> None:
        self._user_repo = user_repo
        self._role_repo = role_repo
        self._hasher = hasher
        self._cache_invalidator = cache_invalidator

    def run(
        self,
        id: str,
        name: str | None = None,
        email: str | None = None,
        password: str | None = None,
        role_id: str | None = None,
    ) -> None:
        user = self._user_repo.find_by_id(IdValueObject(id))
        if user is None:
            raise UserNotFoundError(id)

        if role_id is not None:
            role = self._role_repo.find_by_id(role_id)
            if role is None:
                raise ValueError(f"Role <{role_id}> does not exist")

        if password is not None:
            user.change_password(password, self._hasher)

        user.update(name=name, email=email, role_id=role_id)
        self._user_repo.save(user)
        self._cache_invalidator.invalidate_all()
