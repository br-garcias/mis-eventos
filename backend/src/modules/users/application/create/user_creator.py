from modules.roles.domain.role_repository import RoleRepository
from modules.shared.domain.domain_validation_error import DomainValidationError
from modules.shared.domain.security.password_hasher import PasswordHasher
from modules.shared.domain.value_object.invalid_argument_error import InvalidArgumentError
from modules.users.domain.user import User
from modules.users.domain.user_already_exists_error import UserAlreadyExistsError
from modules.user_views.application.invalidate_cache.invalidate_user_views_cache import (
    InvalidateUserViewsCache,
)
from modules.users.domain.user_password import UserPassword
from modules.users.domain.user_repository import UserRepository


class UserCreator:
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

    def run(self, id: str, name: str, email: str, password: str, role_name: str) -> None:
        if self._user_repo.find_by_email(email):
            raise UserAlreadyExistsError(email)

        role = self._role_repo.find_by_name(role_name)
        if role is None:
            raise DomainValidationError({"role_name": [f"Role <{role_name}> does not exist"]})

        try:
            password_hash = UserPassword.from_plain(password, self._hasher)
        except InvalidArgumentError as e:
            raise DomainValidationError({"password": [str(e)]})

        user = User.create(
            id=id,
            name=name,
            email=email,
            password_hash=password_hash.value,
            role_id=role.id.value,
        )
        self._user_repo.save(user)
        self._cache_invalidator.invalidate_all()
