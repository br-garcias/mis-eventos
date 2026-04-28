"""Unit tests for Event command handlers."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from modules.events.application.cancel.cancel_event_command import CancelEventCommand
from modules.events.application.cancel.cancel_event_command_handler import CancelEventCommandHandler
from modules.events.application.cancel.event_canceller import EventCanceller
from modules.events.application.create.create_event_command import CreateEventCommand
from modules.events.application.create.create_event_command_handler import CreateEventCommandHandler
from modules.events.application.create.event_creator import EventCreator
from modules.events.application.delete.delete_event_command import DeleteEventCommand
from modules.events.application.delete.delete_event_command_handler import DeleteEventCommandHandler
from modules.events.application.delete.event_deleter import EventDeleter
from modules.events.application.publish.event_publisher import EventPublisher
from modules.events.application.publish.publish_event_command import PublishEventCommand
from modules.events.application.publish.publish_event_command_handler import PublishEventCommandHandler
from modules.events.application.update.event_updater import EventUpdater
from modules.events.application.update.update_event_command import UpdateEventCommand
from modules.events.application.update.update_event_command_handler import UpdateEventCommandHandler
from modules.events.application.authorization import EventForbiddenError
from modules.events.domain.errors import EventNotFoundError
from modules.shared.domain.value_object.id_value_object import IdValueObject
from tests.unit.modules._fakes import FakeEventRepository, FakeInvalidateCache, make_event


def _make_repo_with_event():
    repo = FakeEventRepository()
    event = make_event()
    repo.save(event)
    return repo, event


def test_create_event_command_handler():
    repo = FakeEventRepository()
    cache = FakeInvalidateCache()
    handler = CreateEventCommandHandler(EventCreator(repo, cache))
    uid = str(uuid4())
    now = datetime.now(timezone.utc)
    cmd = CreateEventCommand(
        id=uid,
        name="PyCon",
        description="Python conference",
        organizer_id=str(uuid4()),
        capacity=100,
        start_at=now + timedelta(days=1),
        end_at=now + timedelta(days=2),
        location="BOG",
    )
    handler.handle(cmd)
    assert repo.find_by_id(IdValueObject(uid)) is not None
    assert cache.calls == 1


def test_cancel_event_command_handler():
    repo, event = _make_repo_with_event()
    cache = FakeInvalidateCache()
    handler = CancelEventCommandHandler(EventCanceller(repo, cache))
    cmd = CancelEventCommand(id=event.id.value, actor_user_id=event.organizer_id.value, actor_role="organizer")
    handler.handle(cmd)
    updated = repo.find_by_id(event.id)
    assert updated.status.value == "cancelled"
    assert cache.calls == 1


def test_delete_event_command_handler():
    repo, event = _make_repo_with_event()
    cache = FakeInvalidateCache()
    handler = DeleteEventCommandHandler(EventDeleter(repo, cache))
    cmd = DeleteEventCommand(id=event.id.value, actor_user_id=event.organizer_id.value, actor_role="organizer")
    handler.handle(cmd)
    assert repo.find_by_id(event.id) is None
    assert cache.calls == 1


def test_publish_event_command_handler():
    repo, event = _make_repo_with_event()
    cache = FakeInvalidateCache()
    handler = PublishEventCommandHandler(EventPublisher(repo, cache))
    cmd = PublishEventCommand(id=event.id.value, actor_user_id=event.organizer_id.value, actor_role="organizer")
    handler.handle(cmd)
    updated = repo.find_by_id(event.id)
    assert updated.status.value == "published"
    assert cache.calls == 1


def test_update_event_command_handler():
    repo, event = _make_repo_with_event()
    cache = FakeInvalidateCache()
    handler = UpdateEventCommandHandler(EventUpdater(repo, cache))
    cmd = UpdateEventCommand(
        id=event.id.value,
        actor_user_id=event.organizer_id.value,
        actor_role="organizer",
        name="Updated",
    )
    handler.handle(cmd)
    updated = repo.find_by_id(event.id)
    assert updated.name.value == "Updated"
    assert cache.calls == 1


def test_cancel_event_not_found():
    repo = FakeEventRepository()
    cache = FakeInvalidateCache()
    handler = CancelEventCommandHandler(EventCanceller(repo, cache))
    cmd = CancelEventCommand(id=str(uuid4()), actor_user_id=str(uuid4()), actor_role="organizer")
    with pytest.raises(EventNotFoundError):
        handler.handle(cmd)


def test_cancel_event_forbidden():
    repo, event = _make_repo_with_event()
    cache = FakeInvalidateCache()
    handler = CancelEventCommandHandler(EventCanceller(repo, cache))
    cmd = CancelEventCommand(id=event.id.value, actor_user_id=str(uuid4()), actor_role="organizer")
    with pytest.raises(EventForbiddenError):
        handler.handle(cmd)


def test_cancel_event_admin():
    repo, event = _make_repo_with_event()
    cache = FakeInvalidateCache()
    handler = CancelEventCommandHandler(EventCanceller(repo, cache))
    cmd = CancelEventCommand(id=event.id.value, actor_user_id=str(uuid4()), actor_role="admin")
    handler.handle(cmd)
    assert repo.find_by_id(event.id).status.value == "cancelled"


def test_delete_event_not_deletable():
    repo, event = _make_repo_with_event()
    event.publish()
    repo.save(event)
    cache = FakeInvalidateCache()
    handler = DeleteEventCommandHandler(EventDeleter(repo, cache))
    cmd = DeleteEventCommand(id=event.id.value, actor_user_id=event.organizer_id.value, actor_role="organizer")
    from modules.events.domain.errors import EventNotDeletableError
    with pytest.raises(EventNotDeletableError):
        handler.handle(cmd)


def test_publish_event_command_handler_subscribed():
    repo, event = _make_repo_with_event()
    cache = FakeInvalidateCache()
    handler = PublishEventCommandHandler(EventPublisher(repo, cache))
    assert handler.subscribed_to() == PublishEventCommand


def test_update_event_reschedule():
    repo, event = _make_repo_with_event()
    cache = FakeInvalidateCache()
    handler = UpdateEventCommandHandler(EventUpdater(repo, cache))
    now = datetime.now(timezone.utc)
    cmd = UpdateEventCommand(
        id=event.id.value,
        actor_user_id=event.organizer_id.value,
        actor_role="organizer",
        start_at=now + timedelta(days=2),
        end_at=now + timedelta(days=3),
    )
    handler.handle(cmd)
    updated = repo.find_by_id(event.id)
    assert updated.dates.start_at == now + timedelta(days=2)


def test_update_event_capacity():
    repo, event = _make_repo_with_event()
    cache = FakeInvalidateCache()
    handler = UpdateEventCommandHandler(EventUpdater(repo, cache))
    cmd = UpdateEventCommand(
        id=event.id.value,
        actor_user_id=event.organizer_id.value,
        actor_role="organizer",
        capacity=200,
    )
    handler.handle(cmd)
    updated = repo.find_by_id(event.id)
    assert updated.capacity.value == 200
