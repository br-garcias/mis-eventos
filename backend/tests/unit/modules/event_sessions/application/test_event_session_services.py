"""Unit tests for EventSession application services and handlers."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from modules.event_sessions.application.create.create_event_session_command import CreateEventSessionCommand
from modules.event_sessions.application.create.create_event_session_command_handler import CreateEventSessionCommandHandler
from modules.event_sessions.application.create.event_session_creator import EventSessionCreator
from modules.event_sessions.application.delete.delete_event_session_command import DeleteEventSessionCommand
from modules.event_sessions.application.delete.delete_event_session_command_handler import DeleteEventSessionCommandHandler
from modules.event_sessions.application.delete.event_session_deleter import EventSessionDeleter
from modules.event_sessions.application.update.event_session_updater import EventSessionUpdater
from modules.event_sessions.application.update.update_event_session_command import UpdateEventSessionCommand
from modules.event_sessions.application.update.update_event_session_command_handler import UpdateEventSessionCommandHandler
from modules.event_sessions.domain.errors import (
    EventSessionNotFoundError,
    SessionOverlapError,
    SessionTimeOutOfBoundsError,
)
from modules.events.domain.event import Event
from modules.shared.domain.value_object.id_value_object import IdValueObject
from tests.unit.modules._fakes import (
    FakeEventRepository,
    FakeEventSessionRepository,
    FakeInvalidateCache,
    make_event,
)


def _make_event():
    repo = FakeEventRepository()
    event = make_event(capacity=100)
    event.publish()
    repo.save(event)
    return repo, event


def _make_session_repo():
    return FakeEventSessionRepository()


def test_event_session_creator_success():
    event_repo, event = _make_event()
    session_repo = _make_session_repo()
    cache = FakeInvalidateCache()
    creator = EventSessionCreator(event_repo, session_repo, cache)

    sid = str(uuid4())
    start = event.dates.start_at + timedelta(hours=1)
    end = start + timedelta(hours=1)
    creator.run(
        id=sid,
        event_id=event.id.value,
        title="Talk",
        description="Desc",
        speaker_name="Alice",
        speaker_bio="Bio",
        start_at=start,
        end_at=end,
    )

    assert session_repo.find_by_id(IdValueObject(sid)) is not None
    assert cache.calls == 1


def test_event_session_creator_event_not_found():
    event_repo = FakeEventRepository()
    session_repo = _make_session_repo()
    cache = FakeInvalidateCache()
    creator = EventSessionCreator(event_repo, session_repo, cache)

    from modules.events.domain.errors import EventNotFoundError
    with pytest.raises(EventNotFoundError):
        creator.run(
            id=str(uuid4()),
            event_id=str(uuid4()),
            title="Talk",
            description="Desc",
            speaker_name="Alice",
            speaker_bio="Bio",
            start_at=datetime.now(timezone.utc),
            end_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )


def test_event_session_creator_time_out_of_bounds():
    event_repo, event = _make_event()
    session_repo = _make_session_repo()
    cache = FakeInvalidateCache()
    creator = EventSessionCreator(event_repo, session_repo, cache)

    start = event.dates.end_at + timedelta(hours=1)
    end = start + timedelta(hours=1)
    with pytest.raises(SessionTimeOutOfBoundsError):
        creator.run(
            id=str(uuid4()),
            event_id=event.id.value,
            title="Talk",
            description="Desc",
            speaker_name="Alice",
            speaker_bio="Bio",
            start_at=start,
            end_at=end,
        )


def test_event_session_creator_overlap():
    event_repo, event = _make_event()
    session_repo = _make_session_repo()
    cache = FakeInvalidateCache()
    creator = EventSessionCreator(event_repo, session_repo, cache)

    start1 = event.dates.start_at + timedelta(hours=1)
    end1 = start1 + timedelta(hours=2)
    start2 = start1 + timedelta(hours=1)
    end2 = start2 + timedelta(hours=2)
    creator.run(
        id=str(uuid4()),
        event_id=event.id.value,
        title="Talk 1",
        description="Desc",
        speaker_name="Alice",
        speaker_bio="Bio",
        start_at=start1,
        end_at=end1,
    )

    with pytest.raises(SessionOverlapError):
        creator.run(
            id=str(uuid4()),
            event_id=event.id.value,
            title="Talk 2",
            description="Desc",
            speaker_name="Bob",
            speaker_bio="Bio",
            start_at=start2,
            end_at=end2,
        )


def test_event_session_deleter_success():
    event_repo, event = _make_event()
    session_repo = _make_session_repo()
    cache = FakeInvalidateCache()

    from modules.event_sessions.domain.event_session import EventSession
    sid = str(uuid4())
    start = event.dates.start_at + timedelta(hours=1)
    end = start + timedelta(hours=1)
    session = EventSession.create(
        id=sid,
        event_id=event.id.value,
        title="Talk",
        description="Desc",
        speaker_name="Alice",
        speaker_bio="Bio",
        start_at=start,
        end_at=end,
        event_dates=(event.dates.start_at, event.dates.end_at),
    )
    session_repo.save(session)

    deleter = EventSessionDeleter(session_repo, cache)
    deleter.run(id=sid)

    assert session_repo.find_by_id(IdValueObject(sid)) is None
    assert cache.calls == 1


def test_event_session_deleter_not_found():
    session_repo = _make_session_repo()
    cache = FakeInvalidateCache()
    deleter = EventSessionDeleter(session_repo, cache)

    with pytest.raises(EventSessionNotFoundError):
        deleter.run(id=str(uuid4()))


def test_event_session_updater_success():
    event_repo, event = _make_event()
    session_repo = _make_session_repo()
    cache = FakeInvalidateCache()

    from modules.event_sessions.domain.event_session import EventSession
    sid = str(uuid4())
    start = event.dates.start_at + timedelta(hours=1)
    end = start + timedelta(hours=1)
    session = EventSession.create(
        id=sid,
        event_id=event.id.value,
        title="Talk",
        description="Desc",
        speaker_name="Alice",
        speaker_bio="Bio",
        start_at=start,
        end_at=end,
        event_dates=(event.dates.start_at, event.dates.end_at),
    )
    session_repo.save(session)

    updater = EventSessionUpdater(event_repo, session_repo, cache)
    updater.run(
        id=sid,
        title="Updated",
        start_at=start + timedelta(minutes=30),
        end_at=end + timedelta(minutes=30),
    )

    updated = session_repo.find_by_id(IdValueObject(sid))
    assert updated.title.value == "Updated"
    assert cache.calls == 1


def test_event_session_updater_not_found():
    event_repo, event = _make_event()
    session_repo = _make_session_repo()
    cache = FakeInvalidateCache()
    updater = EventSessionUpdater(event_repo, session_repo, cache)

    with pytest.raises(EventSessionNotFoundError):
        updater.run(id=str(uuid4()))


def test_event_session_updater_event_not_found():
    event_repo = FakeEventRepository()
    session_repo = _make_session_repo()
    cache = FakeInvalidateCache()

    from modules.event_sessions.domain.event_session import EventSession
    sid = str(uuid4())
    now = datetime.now(timezone.utc)
    session = EventSession.create(
        id=sid,
        event_id=str(uuid4()),
        title="Talk",
        description="Desc",
        speaker_name="Alice",
        speaker_bio="Bio",
        start_at=now + timedelta(hours=1),
        end_at=now + timedelta(hours=2),
        event_dates=(now, now + timedelta(days=1)),
    )
    session_repo.save(session)

    from modules.events.domain.errors import EventNotFoundError
    updater = EventSessionUpdater(event_repo, session_repo, cache)
    with pytest.raises(EventNotFoundError):
        updater.run(id=sid)


def test_create_event_session_command_handler():
    event_repo, event = _make_event()
    session_repo = _make_session_repo()
    cache = FakeInvalidateCache()
    handler = CreateEventSessionCommandHandler(EventSessionCreator(event_repo, session_repo, cache))

    sid = str(uuid4())
    start = event.dates.start_at + timedelta(hours=1)
    end = start + timedelta(hours=1)
    cmd = CreateEventSessionCommand(
        id=sid,
        event_id=event.id.value,
        title="Talk",
        description="Desc",
        speaker_name="Alice",
        speaker_bio="Bio",
        start_at=start,
        end_at=end,
    )
    handler.handle(cmd)
    assert session_repo.find_by_id(IdValueObject(sid)) is not None


def test_delete_event_session_command_handler():
    event_repo, event = _make_event()
    session_repo = _make_session_repo()
    cache = FakeInvalidateCache()

    from modules.event_sessions.domain.event_session import EventSession
    sid = str(uuid4())
    start = event.dates.start_at + timedelta(hours=1)
    end = start + timedelta(hours=1)
    session = EventSession.create(
        id=sid,
        event_id=event.id.value,
        title="Talk",
        description="Desc",
        speaker_name="Alice",
        speaker_bio="Bio",
        start_at=start,
        end_at=end,
        event_dates=(event.dates.start_at, event.dates.end_at),
    )
    session_repo.save(session)

    handler = DeleteEventSessionCommandHandler(EventSessionDeleter(session_repo, cache))
    cmd = DeleteEventSessionCommand(id=sid)
    handler.handle(cmd)
    assert session_repo.find_by_id(IdValueObject(sid)) is None


def test_update_event_session_command_handler():
    event_repo, event = _make_event()
    session_repo = _make_session_repo()
    cache = FakeInvalidateCache()

    from modules.event_sessions.domain.event_session import EventSession
    sid = str(uuid4())
    start = event.dates.start_at + timedelta(hours=1)
    end = start + timedelta(hours=1)
    session = EventSession.create(
        id=sid,
        event_id=event.id.value,
        title="Talk",
        description="Desc",
        speaker_name="Alice",
        speaker_bio="Bio",
        start_at=start,
        end_at=end,
        event_dates=(event.dates.start_at, event.dates.end_at),
    )
    session_repo.save(session)

    handler = UpdateEventSessionCommandHandler(EventSessionUpdater(event_repo, session_repo, cache))
    cmd = UpdateEventSessionCommand(id=sid, title="Updated")
    handler.handle(cmd)
    assert session_repo.find_by_id(IdValueObject(sid)).title.value == "Updated"
