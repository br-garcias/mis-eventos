from modules.shared.domain.command_bus import CommandBus
from modules.shared.domain.query_bus import QueryBus
from modules.shared.infrastructure.command_bus.in_memory_command_bus import InMemoryCommandBus
from modules.shared.infrastructure.query_bus.in_memory_query_bus import InMemoryQueryBus

from .auth_di import auth_command_handlers, auth_query_handlers
from .event_sessions_di import event_sessions_command_handlers
from .events_di import events_command_handlers, events_query_handlers
from .registration_views_di import registration_views_query_handlers
from .registrations_di import registrations_command_handlers
from .role_views_di import role_views_query_handlers
from .user_views_di import user_views_query_handlers
from .users_di import users_command_handlers

_command_bus: CommandBus = InMemoryCommandBus({
    **users_command_handlers(),
    **auth_command_handlers(),
    **events_command_handlers(),
    **event_sessions_command_handlers(),
    **registrations_command_handlers(),
})

_query_bus: QueryBus = InMemoryQueryBus({
    **auth_query_handlers(),
    **user_views_query_handlers(),
    **events_query_handlers(),
    **registration_views_query_handlers(),
    **role_views_query_handlers(),
})


def get_command_bus() -> CommandBus:
    return _command_bus


def get_query_bus() -> QueryBus:
    return _query_bus
