from typing import Any, Callable, Dict, Type

from modules.event_views.application.find_by_id.event_finder_by_id import EventFinderById
from modules.event_views.application.find_by_id.find_event_by_id_query import (
    FindEventByIdQuery,
)
from modules.event_views.application.find_by_id.find_event_by_id_query_handler import (
    FindEventByIdQueryHandler,
)
from modules.event_views.application.find_by_organizer.event_finder_by_organizer import (
    EventFinderByOrganizer,
)
from modules.event_views.application.find_by_organizer.find_my_events_query import (
    FindMyEventsQuery,
)
from modules.event_views.application.find_by_organizer.find_my_events_query_handler import (
    FindMyEventsQueryHandler,
)
from modules.event_views.application.invalidate_cache.invalidate_event_views_cache import (
    InvalidateEventViewsCache,
)
from modules.event_views.application.search.event_searcher import EventSearcher
from modules.event_views.application.search.search_events_query import SearchEventsQuery
from modules.event_views.application.search.search_events_query_handler import (
    SearchEventsQueryHandler,
)
from modules.event_views.infrastructure.persistence.cached_event_view_repository import (
    CachedEventViewRepository,
)
from modules.event_views.infrastructure.persistence.mongo_event_view_repository import (
    MongoEventViewRepository,
)
from modules.events.application.cancel.cancel_event_command import CancelEventCommand
from modules.events.application.cancel.cancel_event_command_handler import (
    CancelEventCommandHandler,
)
from modules.events.application.cancel.event_canceller import EventCanceller
from modules.events.application.create.create_event_command import CreateEventCommand
from modules.events.application.create.create_event_command_handler import (
    CreateEventCommandHandler,
)
from modules.events.application.create.event_creator import EventCreator
from modules.events.application.delete.delete_event_command import DeleteEventCommand
from modules.events.application.delete.delete_event_command_handler import (
    DeleteEventCommandHandler,
)
from modules.events.application.delete.event_deleter import EventDeleter
from modules.events.application.publish.event_publisher import EventPublisher
from modules.events.application.publish.publish_event_command import PublishEventCommand
from modules.events.application.publish.publish_event_command_handler import (
    PublishEventCommandHandler,
)
from modules.events.application.update.event_updater import EventUpdater
from modules.events.application.update.update_event_command import UpdateEventCommand
from modules.events.application.update.update_event_command_handler import (
    UpdateEventCommandHandler,
)
from modules.events.domain.event_repository import EventRepository
from modules.events.infrastructure.persistence.mongo_event_repository import (
    MongoEventRepository,
)
from apps.api.config import CACHE_TTL_SECONDS
from modules.shared.domain.command import Command
from modules.shared.domain.query import Query

from .cache_di import cache
from .shared_di import mongo_client

event_repository: EventRepository = MongoEventRepository(mongo_client)
event_view_repository = CachedEventViewRepository(
    MongoEventViewRepository(mongo_client), cache, ttl_seconds=CACHE_TTL_SECONDS
)
invalidate_event_views_cache = InvalidateEventViewsCache(event_view_repository)


def events_command_handlers() -> Dict[Type[Command], Callable[[Command], Any]]:
    return {
        CreateEventCommand: CreateEventCommandHandler(
            EventCreator(event_repository, invalidate_event_views_cache)
        ),
        UpdateEventCommand: UpdateEventCommandHandler(
            EventUpdater(event_repository, invalidate_event_views_cache)
        ),
        DeleteEventCommand: DeleteEventCommandHandler(
            EventDeleter(event_repository, invalidate_event_views_cache)
        ),
        PublishEventCommand: PublishEventCommandHandler(
            EventPublisher(event_repository, invalidate_event_views_cache)
        ),
        CancelEventCommand: CancelEventCommandHandler(
            EventCanceller(event_repository, invalidate_event_views_cache)
        ),
    }


def events_query_handlers() -> Dict[Type[Query], Callable[[Query], Any]]:
    event_finder = EventFinderById(event_view_repository)
    event_searcher = EventSearcher(event_view_repository)
    event_finder_by_organizer = EventFinderByOrganizer(event_view_repository)

    return {
        SearchEventsQuery: SearchEventsQueryHandler(event_searcher),
        FindEventByIdQuery: FindEventByIdQueryHandler(event_finder),
        FindMyEventsQuery: FindMyEventsQueryHandler(event_finder_by_organizer),
    }
