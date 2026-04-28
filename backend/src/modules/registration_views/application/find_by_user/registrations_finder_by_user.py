from typing import List

from modules.registration_views.domain.registration_view_repository import (
    RegistrationViewRepository,
)
from modules.registration_views.domain.registration_view_dto import MyRegistrationView


class RegistrationsFinderByUser:
    def __init__(self, view_repository: RegistrationViewRepository) -> None:
        self._view_repository = view_repository

    def run(self, user_id: str) -> List[MyRegistrationView]:
        return self._view_repository.find_by_user(user_id)
