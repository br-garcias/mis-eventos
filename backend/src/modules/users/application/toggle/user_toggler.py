from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.user_views.application.invalidate_cache.invalidate_user_views_cache import (
    InvalidateUserViewsCache,
)
from modules.users.domain.user_repository import UserRepository
from modules.users.domain.user_not_found_error import UserNotFoundError


class UserToggler:
    def __init__(
        self,
        user_repo: UserRepository,
        cache_invalidator: InvalidateUserViewsCache,
    ) -> None:
        self._user_repo = user_repo
        self._cache_invalidator = cache_invalidator

    def run(self, id: str) -> None:
        user = self._user_repo.find_by_id(IdValueObject(id))
        if user is None:
            raise UserNotFoundError(id)
        user.toggle()
        self._user_repo.save(user)
        self._cache_invalidator.invalidate_all()
