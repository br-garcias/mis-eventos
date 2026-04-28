from typing import List

from modules.events.domain.event_repository import EventRepository
from modules.registration_views.domain.registration_view_dto import EventAttendeeView
from modules.shared.domain.query_handler import QueryHandler
from modules.shared.domain.value_object.id_value_object import IdValueObject

from .attendees_finder_by_event import AttendeesFinderByEvent
from .find_attendees_by_event_query import FindAttendeesByEventQuery


class FindAttendeesByEventQueryHandler(QueryHandler):
    def __init__(self, finder: AttendeesFinderByEvent, event_repository: EventRepository) -> None:
        self._finder = finder
        self._event_repository = event_repository

    def subscribed_to(self):
        return FindAttendeesByEventQuery

    def handle(self, query: FindAttendeesByEventQuery) -> List[EventAttendeeView]:
        if query.actor_role not in ("admin", "organizer"):
            return []

        event = self._event_repository.find_by_id(IdValueObject(query.event_id))
        if event is None:
            return []

        if query.actor_role != "admin" and event.organizer_id.value != query.actor_user_id:
            return []

        return self._finder.run(query.event_id)
