"""Unit tests for EventSession aggregate."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from modules.event_sessions.domain.errors import (
    SessionTimeOutOfBoundsError,
)
from modules.event_sessions.domain.event_session import EventSession
from modules.shared.domain.domain_validation_error import DomainValidationError


def _future(days=1):
    return datetime.now(timezone.utc) + timedelta(days=days)


def test_create_event_session_success():
    es = EventSession.create(
        id=str(uuid4()),
        event_id=str(uuid4()),
        title="Keynote",
        description="Opening talk",
        speaker_name="Alice",
        speaker_bio="Expert",
        start_at=_future(1),
        end_at=_future(2),
        event_dates=(_future(0), _future(3)),
    )
    assert es.title.value == "Keynote"


def test_create_event_session_validates_all_fields():
    with pytest.raises(DomainValidationError) as exc:
        EventSession.create(
            id="bad-uuid",
            event_id="bad-uuid",
            title="ab",
            description="x" * 5001,
            speaker_name="Alice",
            speaker_bio="Bio",
            start_at=_future(1),
            end_at=_future(2),
            event_dates=(_future(0), _future(3)),
        )
    assert set(exc.value.errors.keys()) == {"id", "event_id", "title", "description"}


def test_create_event_session_time_out_of_bounds():
    base = _future(0)
    with pytest.raises(DomainValidationError) as exc:
        EventSession.create(
            id=str(uuid4()),
            event_id=str(uuid4()),
            title="Talk",
            description="Desc",
            speaker_name="Bob",
            speaker_bio="Bio",
            start_at=base - timedelta(days=1),
            end_at=base + timedelta(days=1),
            event_dates=(base, base + timedelta(days=1)),
        )
    assert "time_range" in exc.value.errors


def test_update_details():
    es = EventSession.create(
        id=str(uuid4()),
        event_id=str(uuid4()),
        title="Keynote",
        description="Opening talk",
        speaker_name="Alice",
        speaker_bio="Expert",
        start_at=_future(1),
        end_at=_future(2),
        event_dates=(_future(0), _future(3)),
    )
    es.update_details(title="Updated", description="New desc", speaker_name="Bob", speaker_bio="New bio")
    assert es.title.value == "Updated"
    assert es.description.value == "New desc"
    assert es.speaker_name == "Bob"
    assert es.speaker_bio == "New bio"


def test_reschedule():
    es = EventSession.create(
        id=str(uuid4()),
        event_id=str(uuid4()),
        title="Keynote",
        description="Opening talk",
        speaker_name="Alice",
        speaker_bio="Expert",
        start_at=_future(1),
        end_at=_future(2),
        event_dates=(_future(0), _future(3)),
    )
    new_start = _future(1, )
    new_end = _future(2)
    es.reschedule(start_at=new_start, end_at=new_end, event_dates=(_future(0), _future(3)))
    assert es.time_range.start_at == new_start


def test_reschedule_out_of_bounds():
    es = EventSession.create(
        id=str(uuid4()),
        event_id=str(uuid4()),
        title="Keynote",
        description="Opening talk",
        speaker_name="Alice",
        speaker_bio="Expert",
        start_at=_future(1),
        end_at=_future(2),
        event_dates=(_future(0), _future(3)),
    )
    with pytest.raises(SessionTimeOutOfBoundsError):
        es.reschedule(start_at=_future(4), end_at=_future(5), event_dates=(_future(0), _future(3)))


def test_update_details_invalid_title():
    es = EventSession.create(
        id=str(uuid4()),
        event_id=str(uuid4()),
        title="Keynote",
        description="Opening talk",
        speaker_name="Alice",
        speaker_bio="Expert",
        start_at=_future(1),
        end_at=_future(2),
        event_dates=(_future(0), _future(3)),
    )
    with pytest.raises(DomainValidationError) as exc:
        es.update_details(title="ab")
    assert "title" in exc.value.errors


def test_update_details_no_changes():
    es = EventSession.create(
        id=str(uuid4()),
        event_id=str(uuid4()),
        title="Keynote",
        description="Opening talk",
        speaker_name="Alice",
        speaker_bio="Expert",
        start_at=_future(1),
        end_at=_future(2),
        event_dates=(_future(0), _future(3)),
    )
    old_updated = es.updated_at
    es.update_details()
    assert es.updated_at > old_updated


def test_reschedule_invalid_dates():
    es = EventSession.create(
        id=str(uuid4()),
        event_id=str(uuid4()),
        title="Keynote",
        description="Opening talk",
        speaker_name="Alice",
        speaker_bio="Expert",
        start_at=_future(1),
        end_at=_future(2),
        event_dates=(_future(0), _future(3)),
    )
    with pytest.raises(DomainValidationError) as exc:
        es.reschedule(start_at=_future(2), end_at=_future(1), event_dates=(_future(0), _future(3)))
    assert "time_range" in exc.value.errors


def test_create_event_session_overlaps_with_existing():
    event_id = str(uuid4())
    base = _future(0)
    s1 = EventSession.create(
        id=str(uuid4()),
        event_id=event_id,
        title="Session 1",
        description="Desc",
        speaker_name="Alice",
        speaker_bio="Bio",
        start_at=base + timedelta(hours=1),
        end_at=base + timedelta(hours=2),
        event_dates=(base, base + timedelta(days=1)),
    )
    # This should create successfully since it does not check overlap at creation time
    assert s1.title.value == "Session 1"


def test_create_event_session_missing_speaker():
    es = EventSession.create(
        id=str(uuid4()),
        event_id=str(uuid4()),
        title="Keynote",
        description="Opening talk",
        speaker_name="",
        speaker_bio="",
        start_at=_future(1),
        end_at=_future(2),
        event_dates=(_future(0), _future(3)),
    )
    assert es.speaker_name == ""
    assert es.speaker_bio == ""


def test_create_event_session_description_empty():
    es = EventSession.create(
        id=str(uuid4()),
        event_id=str(uuid4()),
        title="Keynote",
        description="",
        speaker_name="Alice",
        speaker_bio="Expert",
        start_at=_future(1),
        end_at=_future(2),
        event_dates=(_future(0), _future(3)),
    )
    assert es.description.value == ""
