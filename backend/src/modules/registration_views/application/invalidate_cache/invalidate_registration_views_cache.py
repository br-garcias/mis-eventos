from modules.registration_views.domain.registration_view_repository import (
    RegistrationViewRepository,
)


class InvalidateRegistrationViewsCache:
    def __init__(self, repository: RegistrationViewRepository) -> None:
        self._repository = repository

    def invalidate_all(self) -> None:
        self._repository.invalidate_cache()
