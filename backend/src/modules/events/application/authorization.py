from __future__ import annotations

from modules.events.domain.event import Event
from modules.events.domain.errors import EventNotFoundError
from modules.events.domain.event_repository import EventRepository
from modules.shared.domain.domain_error import AuthorizationError
from modules.shared.domain.value_object.id_value_object import IdValueObject


class EventForbiddenError(AuthorizationError): ...


def load_event_for_actor(
    repo: EventRepository,
    *,
    event_id: str,
    actor_user_id: str,
    actor_role: str,
) -> Event:
    event = repo.find_by_id(IdValueObject(event_id))
    if event is None:
        raise EventNotFoundError(event_id)
    if actor_role == "admin":
        return event
    if event.organizer_id.value != actor_user_id:
        raise EventForbiddenError(
            f"User <{actor_user_id}> is not the organiser of event <{event_id}>"
        )
    return event
