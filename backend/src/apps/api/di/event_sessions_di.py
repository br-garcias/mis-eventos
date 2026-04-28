from typing import Any, Callable, Dict, Type

from modules.event_sessions.application.create.create_event_session_command import (
    CreateEventSessionCommand,
)
from modules.event_sessions.application.create.create_event_session_command_handler import (
    CreateEventSessionCommandHandler,
)
from modules.event_sessions.application.create.event_session_creator import (
    EventSessionCreator,
)
from modules.event_sessions.application.delete.delete_event_session_command import (
    DeleteEventSessionCommand,
)
from modules.event_sessions.application.delete.delete_event_session_command_handler import (
    DeleteEventSessionCommandHandler,
)
from modules.event_sessions.application.delete.event_session_deleter import (
    EventSessionDeleter,
)
from modules.event_sessions.application.update.event_session_updater import (
    EventSessionUpdater,
)
from modules.event_sessions.application.update.update_event_session_command import (
    UpdateEventSessionCommand,
)
from modules.event_sessions.application.update.update_event_session_command_handler import (
    UpdateEventSessionCommandHandler,
)
from modules.event_sessions.domain.event_session_repository import (
    EventSessionRepository,
)
from modules.event_sessions.infrastructure.persistence.mongo_event_session_repository import (
    MongoEventSessionRepository,
)
from modules.event_views.application.invalidate_cache.invalidate_event_views_cache import (
    InvalidateEventViewsCache,
)
from modules.event_views.infrastructure.persistence.cached_event_view_repository import (
    CachedEventViewRepository,
)
from modules.event_views.infrastructure.persistence.mongo_event_view_repository import (
    MongoEventViewRepository,
)
from modules.shared.domain.command import Command

from .cache_di import cache
from .shared_di import mongo_client
from .events_di import event_repository

session_repo: EventSessionRepository = MongoEventSessionRepository(mongo_client)

_event_view_repo = CachedEventViewRepository(
    MongoEventViewRepository(mongo_client), cache
)
invalidate_event_views_cache = InvalidateEventViewsCache(_event_view_repo)


def event_sessions_command_handlers() -> Dict[Type[Command], Callable[[Command], Any]]:
    return {
        CreateEventSessionCommand: CreateEventSessionCommandHandler(
            EventSessionCreator(
                event_repo=event_repository,
                session_repo=session_repo,
                cache_invalidator=invalidate_event_views_cache,
            )
        ),
        UpdateEventSessionCommand: UpdateEventSessionCommandHandler(
            EventSessionUpdater(
                event_repo=event_repository,
                session_repo=session_repo,
                cache_invalidator=invalidate_event_views_cache,
            )
        ),
        DeleteEventSessionCommand: DeleteEventSessionCommandHandler(
            EventSessionDeleter(session_repo, invalidate_event_views_cache)
        ),
    }
