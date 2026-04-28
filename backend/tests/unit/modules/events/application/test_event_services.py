"""Unit tests for Event application services."""
from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from modules.event_views.application.invalidate_cache.invalidate_event_views_cache import (
    InvalidateEventViewsCache,
)
from modules.event_views.domain.event_view_repository import EventViewRepository
from modules.events.application.cancel.event_canceller import EventCanceller
from modules.events.application.create.event_creator import EventCreator
from modules.events.application.delete.event_deleter import EventDeleter
from modules.events.application.publish.event_publisher import EventPublisher
from modules.events.application.update.event_updater import EventUpdater
from modules.events.application.authorization import EventForbiddenError
from modules.events.domain.errors import (
    EventNotDeletableError,
    EventNotEditableError,
    EventNotFoundError,
    EventNotPublishableError,
    InvalidEventStatusTransitionError,
)
from tests.unit.modules._fakes import FakeEventRepository, make_event


class FakeEventViewRepository(EventViewRepository):
    def search(self, *, q=None, status=None, organizer_id=None, date_from=None, date_to=None,
               sort_by=None, page=None, size=None):
        return []

    def find_by_id(self, id):
        return None

    def invalidate_cache(self) -> None:
        pass


def _future(days=1):
    return datetime.now() + timedelta(days=days)


def _cache_inv():
    return InvalidateEventViewsCache(FakeEventViewRepository())


class TestEventCreator:
    def test_create_event_persists(self):
        repo = FakeEventRepository()
        creator = EventCreator(repo, _cache_inv())

        event_id = str(uuid4())
        creator.run(
            id=event_id,
            name="PyCon",
            description="Python conference",
            organizer_id=str(uuid4()),
            capacity=100,
            start_at=_future(1),
            end_at=_future(2),
            location="BOG",
        )

        assert event_id in repo._by_id
        assert repo._by_id[event_id].status.value == "draft"


class TestEventUpdater:
    def test_update_details_success(self):
        repo = FakeEventRepository()
        event = make_event()
        repo.save(event)

        updater = EventUpdater(repo, _cache_inv())
        updater.run(
            id=event.id.value,
            actor_user_id=event.organizer_id.value,
            actor_role="organizer",
            name="Updated Name",
            description="Updated Desc",
            location="MED",
            start_at=None,
            end_at=None,
            capacity=None,
        )

        updated = repo._by_id[event.id.value]
        assert updated.name.value == "Updated Name"
        assert updated.description.value == "Updated Desc"
        assert updated.location == "MED"

    def test_reschedule_success(self):
        repo = FakeEventRepository()
        event = make_event()
        repo.save(event)

        new_start = _future(3)
        new_end = _future(4)

        updater = EventUpdater(repo, _cache_inv())
        updater.run(
            id=event.id.value,
            actor_user_id=event.organizer_id.value,
            actor_role="organizer",
            name=None,
            description=None,
            location=None,
            start_at=new_start,
            end_at=new_end,
            capacity=None,
        )

        updated = repo._by_id[event.id.value]
        assert updated.dates.start_at == new_start
        assert updated.dates.end_at == new_end

    def test_change_capacity_success(self):
        repo = FakeEventRepository()
        event = make_event(capacity=100)
        repo.save(event)

        updater = EventUpdater(repo, _cache_inv())
        updater.run(
            id=event.id.value,
            actor_user_id=event.organizer_id.value,
            actor_role="organizer",
            name=None,
            description=None,
            location=None,
            start_at=None,
            end_at=None,
            capacity=50,
        )

        updated = repo._by_id[event.id.value]
        assert updated.capacity.value == 50

    def test_admin_can_update_any_event(self):
        repo = FakeEventRepository()
        event = make_event()
        repo.save(event)

        updater = EventUpdater(repo, _cache_inv())
        updater.run(
            id=event.id.value,
            actor_user_id=str(uuid4()),
            actor_role="admin",
            name="Admin Updated",
            description=None,
            location=None,
            start_at=None,
            end_at=None,
            capacity=None,
        )

        assert repo._by_id[event.id.value].name.value == "Admin Updated"

    def test_non_owner_non_admin_raises_forbidden(self):
        repo = FakeEventRepository()
        event = make_event()
        repo.save(event)

        updater = EventUpdater(repo, _cache_inv())
        with pytest.raises(EventForbiddenError):
            updater.run(
                id=event.id.value,
                actor_user_id=str(uuid4()),
                actor_role="organizer",
                name="Hacked",
                description=None,
                location=None,
                start_at=None,
                end_at=None,
                capacity=None,
            )

    def test_update_ongoing_event_raises(self):
        repo = FakeEventRepository()
        event = make_event()
        event.publish()
        event.mark_ongoing()
        repo.save(event)

        updater = EventUpdater(repo, _cache_inv())
        with pytest.raises(EventNotEditableError):
            updater.run(
                id=event.id.value,
                actor_user_id=event.organizer_id.value,
                actor_role="organizer",
                name="Too Late",
                description=None,
                location=None,
                start_at=None,
                end_at=None,
                capacity=None,
            )


class TestEventPublisher:
    def test_publish_success(self):
        repo = FakeEventRepository()
        event = make_event(capacity=10)
        repo.save(event)

        publisher = EventPublisher(repo, _cache_inv())
        publisher.run(
            id=event.id.value,
            actor_user_id=event.organizer_id.value,
            actor_role="organizer",
        )

        assert repo._by_id[event.id.value].status.value == "published"

    def test_publish_already_published_raises(self):
        repo = FakeEventRepository()
        event = make_event()
        event.publish()
        repo.save(event)

        publisher = EventPublisher(repo, _cache_inv())
        with pytest.raises(InvalidEventStatusTransitionError):
            publisher.run(
                id=event.id.value,
                actor_user_id=event.organizer_id.value,
                actor_role="organizer",
            )


class TestEventCanceller:
    def test_cancel_success(self):
        repo = FakeEventRepository()
        event = make_event()
        event.publish()
        repo.save(event)

        canceller = EventCanceller(repo, _cache_inv())
        canceller.run(
            id=event.id.value,
            actor_user_id=event.organizer_id.value,
            actor_role="organizer",
        )

        assert repo._by_id[event.id.value].status.value == "cancelled"

    def test_cancel_finished_raises(self):
        repo = FakeEventRepository()
        event = make_event()
        event.publish()
        event.mark_ongoing()
        event.finish()
        repo.save(event)

        canceller = EventCanceller(repo, _cache_inv())
        with pytest.raises(InvalidEventStatusTransitionError):
            canceller.run(
                id=event.id.value,
                actor_user_id=event.organizer_id.value,
                actor_role="organizer",
            )


class TestEventDeleter:
    def test_delete_draft_success(self):
        repo = FakeEventRepository()
        event = make_event()
        repo.save(event)

        deleter = EventDeleter(repo, _cache_inv())
        deleter.run(
            id=event.id.value,
            actor_user_id=event.organizer_id.value,
            actor_role="organizer",
        )

        assert event.id.value not in repo._by_id

    def test_delete_published_raises(self):
        repo = FakeEventRepository()
        event = make_event()
        event.publish()
        repo.save(event)

        deleter = EventDeleter(repo, _cache_inv())
        with pytest.raises(EventNotDeletableError):
            deleter.run(
                id=event.id.value,
                actor_user_id=event.organizer_id.value,
                actor_role="organizer",
            )

    def test_delete_nonexistent_raises_not_found(self):
        repo = FakeEventRepository()
        deleter = EventDeleter(repo, _cache_inv())

        with pytest.raises(EventNotFoundError):
            deleter.run(
                id=str(uuid4()),
                actor_user_id=str(uuid4()),
                actor_role="organizer",
            )
