"""Unit tests for Registration Views query handlers and DTOs."""
from datetime import datetime, timezone
from uuid import uuid4

from modules.registration_views.application.find_by_event.attendees_finder_by_event import AttendeesFinderByEvent
from modules.registration_views.application.find_by_event.find_attendees_by_event_query import FindAttendeesByEventQuery
from modules.registration_views.application.find_by_event.find_attendees_by_event_query_handler import FindAttendeesByEventQueryHandler
from modules.registration_views.application.find_by_user.find_registrations_by_user_query import FindRegistrationsByUserQuery
from modules.registration_views.application.find_by_user.find_registrations_by_user_query_handler import FindRegistrationsByUserQueryHandler
from modules.registration_views.application.find_by_user.registrations_finder_by_user import RegistrationsFinderByUser
from modules.registration_views.domain.registration_view_dto import EventAttendeeView, MyRegistrationView, UserView
from modules.registration_views.domain.registration_view_repository import RegistrationViewRepository


class FakeRegistrationViewRepository(RegistrationViewRepository):
    def __init__(self):
        self._data: list[MyRegistrationView] = []
        self._attendees: list[EventAttendeeView] = []
        self._by_user: dict[str, list[MyRegistrationView]] = {}
        self._by_event: dict[str, list[EventAttendeeView]] = {}

    def add(self, user_id: str, reg: MyRegistrationView):
        self._data.append(reg)
        self._by_user.setdefault(user_id, []).append(reg)

    def add_attendee(self, event_id: str, a: EventAttendeeView):
        self._attendees.append(a)
        self._by_event.setdefault(event_id, []).append(a)

    def find_by_user(self, user_id: str, status: str | None = None):
        results = self._by_user.get(user_id, [])
        if status is not None:
            results = [r for r in results if r.status == status]
        return results

    def find_by_event(self, event_id: str, status: str | None = None):
        # Support both registration queries and attendee queries
        attendees = self._by_event.get(event_id, [])
        if attendees:
            return attendees
        return [r for r in self._data if r.event_id == event_id and (status is None or r.status == status)]

    def find_by_id(self, registration_id: str):
        for r in self._data:
            if r.id == registration_id:
                return r
        return None

    def find_attendees_by_event(self, event_id: str):
        return self._by_event.get(event_id, [])

    def invalidate_cache(self):
        pass


def _make_registration():
    now = datetime.now(timezone.utc)
    return MyRegistrationView(
        id=str(uuid4()),
        event={
            "id": str(uuid4()),
            "name": "PyCon",
            "description": "Python Conference",
            "start_at": now.isoformat(),
            "end_at": now.isoformat(),
            "location": "BOG",
            "status": "published",
        },
        status="confirmed",
        created_at=now,
        updated_at=now,
    )


def test_find_registrations_by_user_query_handler():
    repo = FakeRegistrationViewRepository()
    reg = _make_registration()
    uid = str(uuid4())
    repo.add(uid, reg)

    finder = RegistrationsFinderByUser(repo)
    handler = FindRegistrationsByUserQueryHandler(finder)

    result = handler.handle(FindRegistrationsByUserQuery(user_id=uid))
    assert len(result) == 1
    assert result[0].id == reg.id
    assert handler.subscribed_to() == FindRegistrationsByUserQuery


def test_find_attendees_by_event_query_handler():
    repo = FakeRegistrationViewRepository()
    now = datetime.now(timezone.utc)
    user_id = str(uuid4())
    attendee = EventAttendeeView(
        id=str(uuid4()),
        user=UserView(
            id=user_id,
            name="Alice",
            email="alice@example.com",
        ),
        status="confirmed",
        created_at=now,
        updated_at=now,
    )
    event_id = str(uuid4())
    repo.add_attendee(event_id, attendee)

    finder = AttendeesFinderByEvent(repo)

    class FakeEventRepository:
        def find_by_id(self, event_id):
            from modules.shared.domain.value_object.id_value_object import IdValueObject
            class FakeEvent:
                def __init__(self, oid):
                    self.organizer_id = IdValueObject("00000000-0000-0000-0000-000000000001")
            return FakeEvent("org-1")

    handler = FindAttendeesByEventQueryHandler(finder, FakeEventRepository())

    result = handler.handle(FindAttendeesByEventQuery(
        event_id=event_id,
        actor_user_id="00000000-0000-0000-0000-000000000001",
        actor_role="organizer",
    ))
    assert len(result) == 1
    assert result[0].user.name == "Alice"
    assert handler.subscribed_to() == FindAttendeesByEventQuery


def test_registration_view_to_primitive():
    reg = _make_registration()
    d = reg.to_primitive()
    assert d["status"] == "confirmed"


def test_registration_view_from_primitive():
    now = datetime.now(timezone.utc)
    d = {
        "id": "r1",
        "event_id": "e1",
        "event_name": "PyCon",
        "event_start_at": now.isoformat(),
        "event_end_at": now.isoformat(),
        "event_location": "BOG",
        "event_status": "published",
        "status": "cancelled",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }
    reg = MyRegistrationView.from_primitive(d)
    assert reg.status == "cancelled"


def test_event_attendee_view_to_primitive():
    now = datetime.now(timezone.utc)
    a = EventAttendeeView(
        id="r1",
        user=UserView(id="u1", name="Alice", email="a@e.com"),
        status="confirmed",
        created_at=now,
        updated_at=now,
    )
    d = a.to_primitive()
    assert d["user"]["name"] == "Alice"
    assert d["user"]["id"] == "u1"


def test_event_attendee_view_from_primitive():
    now = datetime.now(timezone.utc).isoformat()
    d = {
        "id": "r1",
        "user": {"id": "u1", "name": "Alice", "email": "a@e.com"},
        "status": "confirmed",
        "created_at": now,
        "updated_at": now,
    }
    a = EventAttendeeView.from_primitive(d)
    assert a.user.email == "a@e.com"
    assert a.user.name == "Alice"
