"""Unit tests for Event Views query handlers and DTOs."""
from datetime import datetime, timezone
from uuid import uuid4

from modules.event_views.application.find_by_id.event_finder_by_id import EventFinderById
from modules.event_views.application.find_by_id.find_event_by_id_query import FindEventByIdQuery
from modules.event_views.application.find_by_id.find_event_by_id_query_handler import FindEventByIdQueryHandler
from modules.event_views.application.find_by_organizer.event_finder_by_organizer import EventFinderByOrganizer
from modules.event_views.application.find_by_organizer.find_my_events_query import FindMyEventsQuery
from modules.event_views.application.find_by_organizer.find_my_events_query_handler import FindMyEventsQueryHandler
from modules.event_views.application.search.event_searcher import EventSearcher
from modules.event_views.application.search.search_events_query import SearchEventsQuery
from modules.event_views.application.search.search_events_query_handler import SearchEventsQueryHandler
from modules.event_views.domain.event_view_dto import (
    EventDetailView,
    EventSessionSummaryView,
    EventSummaryView,
    OrganizerView,
    Page,
)
from modules.event_views.domain.event_view_repository import EventViewRepository


class FakeEventViewRepository(EventViewRepository):
    def __init__(self):
        self._events: dict[str, EventDetailView] = {}

    def add(self, event: EventDetailView):
        self._events[event.id] = event

    def search(self, **kwargs):
        items = [
            EventSummaryView(
                id=e.id,
                name=e.name,
                description=e.description,
                organizer=e.organizer,
                status=e.status,
                capacity=e.capacity,
                confirmed_attendees=e.confirmed_attendees,
                available_spots=e.available_spots,
                start_at=e.start_at,
                end_at=e.end_at,
                location=e.location,
            )
            for e in self._events.values()
        ]
        return Page(items=items, total=len(items), page=1, size=20)

    def find_by_id(self, id: str, user_id: str | None = None):
        return self._events.get(id)

    def find_by_organizer(self, organizer_id: str, q: str | None = None, status: str | None = None, page: int = 1, size: int = 20):
        items = [
            EventSummaryView(
                id=e.id,
                name=e.name,
                description=e.description,
                organizer=e.organizer,
                status=e.status,
                capacity=e.capacity,
                confirmed_attendees=e.confirmed_attendees,
                available_spots=e.available_spots,
                start_at=e.start_at,
                end_at=e.end_at,
                location=e.location,
            )
            for e in self._events.values()
            if e.organizer.id == organizer_id
            and (q is None or q.lower() in e.name.lower())
            and (status is None or e.status == status)
        ]
        return Page(items=items, total=len(items), page=page, size=size)

    def invalidate_cache(self):
        pass


def _make_detail():
    now = datetime.now(timezone.utc)
    return EventDetailView(
        id=str(uuid4()),
        name="PyCon",
        description="Python conf",
        organizer=OrganizerView(id=str(uuid4()), name="Organizer", email="org@test.com"),
        status="published",
        capacity=100,
        confirmed_attendees=50,
        available_spots=50,
        start_at=now,
        end_at=now,
        location="BOG",
        sessions=[],
        created_at=now,
        updated_at=now,
    )


def test_find_event_by_id_query_handler():
    repo = FakeEventViewRepository()
    event = _make_detail()
    repo.add(event)

    finder = EventFinderById(repo)
    handler = FindEventByIdQueryHandler(finder)

    result = handler.handle(FindEventByIdQuery(id=event.id))
    assert result is not None
    assert result.name == "PyCon"
    assert handler.subscribed_to() == FindEventByIdQuery


def test_search_events_query_handler():
    repo = FakeEventViewRepository()
    event = _make_detail()
    repo.add(event)

    searcher = EventSearcher(repo)
    handler = SearchEventsQueryHandler(searcher)

    result = handler.handle(SearchEventsQuery())
    assert len(result.items) == 1
    assert result.items[0].name == "PyCon"
    assert handler.subscribed_to() == SearchEventsQuery


def test_event_detail_view_to_primitive():
    event = _make_detail()
    d = event.to_primitive()
    assert d["name"] == "PyCon"
    assert d["created_at"] == event.created_at.isoformat()


def test_event_summary_view_from_primitive():
    now = datetime.now(timezone.utc).isoformat()
    d = {
        "id": "e1",
        "name": "Test",
        "organizer": {"id": "o1", "name": "Org", "email": "org@test.com"},
        "status": "published",
        "capacity": 100,
        "confirmed_attendees": 50,
        "available_spots": 50,
        "start_at": now,
        "end_at": now,
        "location": "BOG",
        "description": "Test event",
    }
    e = EventSummaryView.from_primitive(d)
    assert e.name == "Test"


def test_page_to_primitive():
    now = datetime.now(timezone.utc)
    e = EventSummaryView(
        id="e1", name="Test", description="Test event",
        organizer=OrganizerView(id="o1", name="Org", email="org@test.com"),
        status="published",
        capacity=100, confirmed_attendees=50, available_spots=50,
        start_at=now, end_at=now, location="BOG",
    )
    page = Page(items=[e], total=1, page=1, size=20)
    d = page.to_primitive()
    assert d["total"] == 1
    assert d["items"][0]["name"] == "Test"


def test_page_from_primitive():
    now = datetime.now(timezone.utc).isoformat()
    d = {
        "items": [
            {
                "id": "e1",
                "name": "Test",
                "organizer_id": "o1",
                "status": "published",
                "capacity": 100,
                "confirmed_attendees": 50,
                "available_spots": 50,
                "start_at": now,
                "end_at": now,
                "location": "BOG",
            }
        ],
        "total": 1,
        "page": 1,
        "size": 20,
    }
    page = Page.from_primitive(d, EventSummaryView.from_primitive)
    assert len(page.items) == 1
    assert page.items[0].name == "Test"


def test_find_my_events_query_handler():
    organizer_id = str(uuid4())
    now = datetime.now(timezone.utc)
    event = EventDetailView(
        id=str(uuid4()),
        name="My Event",
        description="My event desc",
        organizer=OrganizerView(id=organizer_id, name="Organizer", email="org@test.com"),
        status="published",
        capacity=100,
        confirmed_attendees=50,
        available_spots=50,
        start_at=now,
        end_at=now,
        location="BOG",
        sessions=[],
        created_at=now,
        updated_at=now,
    )

    repo = FakeEventViewRepository()
    repo.add(event)

    finder = EventFinderByOrganizer(repo)
    handler = FindMyEventsQueryHandler(finder)

    result = handler.handle(FindMyEventsQuery(organizer_id=organizer_id))
    assert len(result.items) == 1
    assert result.items[0].name == "My Event"
    assert handler.subscribed_to() == FindMyEventsQuery


def test_find_my_events_query_handler_with_status_filter():
    organizer_id = str(uuid4())
    now = datetime.now(timezone.utc)

    event1 = EventDetailView(
        id=str(uuid4()),
        name="Published Event",
        description="desc",
        organizer=OrganizerView(id=organizer_id, name="Org", email="org@test.com"),
        status="published",
        capacity=100,
        confirmed_attendees=50,
        available_spots=50,
        start_at=now,
        end_at=now,
        location="BOG",
        sessions=[],
        created_at=now,
        updated_at=now,
    )
    event2 = EventDetailView(
        id=str(uuid4()),
        name="Draft Event",
        description="desc",
        organizer=OrganizerView(id=organizer_id, name="Org", email="org@test.com"),
        status="draft",
        capacity=100,
        confirmed_attendees=0,
        available_spots=100,
        start_at=now,
        end_at=now,
        location="BOG",
        sessions=[],
        created_at=now,
        updated_at=now,
    )

    repo = FakeEventViewRepository()
    repo.add(event1)
    repo.add(event2)

    finder = EventFinderByOrganizer(repo)
    handler = FindMyEventsQueryHandler(finder)

    result = handler.handle(FindMyEventsQuery(organizer_id=organizer_id, status="published"))
    assert len(result.items) == 1
    assert result.items[0].name == "Published Event"
