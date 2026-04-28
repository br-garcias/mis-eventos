from typing import List

from modules.registration_views.domain.registration_view_repository import (
    RegistrationViewRepository,
)
from modules.registration_views.domain.registration_view_dto import EventAttendeeView


class AttendeesFinderByEvent:
    def __init__(self, view_repository: RegistrationViewRepository) -> None:
        self._view_repository = view_repository

    def run(self, event_id: str) -> List[EventAttendeeView]:
        return self._view_repository.find_by_event(event_id)
