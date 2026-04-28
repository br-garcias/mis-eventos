from typing import Any, Callable, Dict, Type

from modules.registration_views.application.find_by_event.attendees_finder_by_event import AttendeesFinderByEvent
from modules.registration_views.application.find_by_event.find_attendees_by_event_query import FindAttendeesByEventQuery
from modules.registration_views.application.find_by_event.find_attendees_by_event_query_handler import FindAttendeesByEventQueryHandler
from modules.registration_views.application.find_by_user.find_registrations_by_user_query import FindRegistrationsByUserQuery
from modules.registration_views.application.find_by_user.find_registrations_by_user_query_handler import FindRegistrationsByUserQueryHandler
from modules.registration_views.application.find_by_user.registrations_finder_by_user import RegistrationsFinderByUser
from modules.registration_views.domain.registration_view_repository import RegistrationViewRepository
from modules.registration_views.infrastructure.persistence.cached_registration_view_repository import CachedRegistrationViewRepository
from modules.registration_views.infrastructure.persistence.mongo_registration_view_repository import MongoRegistrationViewRepository
from apps.api.config import CACHE_TTL_SECONDS
from modules.shared.domain.query import Query

from .cache_di import cache
from .events_di import event_repository
from .shared_di import mongo_client


def registration_view_repository() -> RegistrationViewRepository:
    inner = MongoRegistrationViewRepository(mongo_client)
    return CachedRegistrationViewRepository(
        inner, cache, ttl_seconds=CACHE_TTL_SECONDS
    )


def registration_views_query_handlers() -> Dict[Type[Query], Callable[[Query], Any]]:
    repo = registration_view_repository()
    finder_by_user = RegistrationsFinderByUser(repo)
    finder_by_event = AttendeesFinderByEvent(repo)

    return {
        FindRegistrationsByUserQuery: FindRegistrationsByUserQueryHandler(finder_by_user),
        FindAttendeesByEventQuery: FindAttendeesByEventQueryHandler(finder_by_event, event_repository),
    }
