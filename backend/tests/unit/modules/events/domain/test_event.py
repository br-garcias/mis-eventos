"""Unit tests for Event aggregate invariants."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from modules.events.domain.event import Event
from modules.events.domain.errors import (
    InvalidEventStatusTransitionError,
    EventNotEditableError,
    EventNotPublishableError,
    EventNotDeletableError,
    EventCapacityBelowConfirmedError,
    EventFullError,
    EventNotPublishedError,
    EventNotFoundError,
)
from modules.events.domain.event_capacity import EventCapacity
from modules.events.domain.event_date_range import EventDateRange
from modules.events.domain.event_description import EventDescription
from modules.events.domain.event_name import EventName
from modules.events.domain.event_status import EventStatus
from modules.shared.domain.domain_validation_error import DomainValidationError
from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.shared.domain.value_object.invalid_argument_error import InvalidArgumentError


def _future(days=1):
    return datetime.now(timezone.utc) + timedelta(days=days)


def test_create_event_success():
    e = Event.create(
        id=str(uuid4()),
        name="PyCon",
        description="A Python conference",
        organizer_id=str(uuid4()),
        capacity=100,
        start_at=_future(1),
        end_at=_future(2),
        location="BOG",
    )
    assert e.status.value == "draft"
    assert e.available_spots == 100


def test_event_transitions():
    e = Event.create(
        id=str(uuid4()), name="Test", description="", organizer_id=str(uuid4()),
        capacity=10, start_at=_future(1), end_at=_future(2), location="BOG",
    )
    e.publish()
    assert e.status.value == "published"

    with pytest.raises(InvalidEventStatusTransitionError):
        e.publish()

    e.mark_ongoing()
    assert e.status.value == "ongoing"
    e.finish()
    assert e.status.value == "finished"


def test_event_not_editable_after_publish():
    e = Event.create(
        id=str(uuid4()), name="Test", description="", organizer_id=str(uuid4()),
        capacity=10, start_at=_future(1), end_at=_future(2), location="BOG",
    )
    e.publish()
    # PUBLISHED is editable; ONGOING is not
    e.mark_ongoing()
    with pytest.raises(EventNotEditableError):
        e.update_details(name="Updated")


def test_reserve_release_spots():
    e = Event.create(
        id=str(uuid4()), name="Test", description="", organizer_id=str(uuid4()),
        capacity=2, start_at=_future(1), end_at=_future(2), location="BOG",
    )
    e.publish()
    e.reserve_spot()
    assert e.available_spots == 1
    e.reserve_spot()
    assert e.available_spots == 0
    e.release_spot()
    assert e.available_spots == 1


def test_create_event_validates_all_fields():
    with pytest.raises(DomainValidationError) as exc:
        Event.create(
            id="bad-uuid",
            name="ab",
            description="x" * 5001,
            organizer_id="bad-uuid",
            capacity=0,
            start_at=_future(2),
            end_at=_future(1),
            location="BOG",
        )
    assert set(exc.value.errors.keys()) == {"id", "name", "description", "organizer_id", "capacity", "dates"}


def test_event_from_persistence():
    now = datetime.now(timezone.utc)
    e = Event.from_persistence(
        id=Event.create(id=str(uuid4()), name="Test", description="", organizer_id=str(uuid4()),
                        capacity=10, start_at=_future(1), end_at=_future(2), location="BOG").id,
        name=EventName("Test"),
        description=EventDescription("Desc"),
        organizer_id=Event.create(id=str(uuid4()), name="Org", description="", organizer_id=str(uuid4()),
                                  capacity=10, start_at=_future(1), end_at=_future(2), location="BOG").organizer_id,
        capacity=EventCapacity(10),
        confirmed_attendees=0,
        dates=EventDateRange(start_at=now, end_at=now + timedelta(days=1)),
        location="BOG",
        status=EventStatus.DRAFT,
        created_at=now,
        updated_at=now,
    )
    assert e.status.value == "draft"


def test_event_transitions_invalid():
    e = Event.create(
        id=str(uuid4()), name="Test", description="", organizer_id=str(uuid4()),
        capacity=10, start_at=_future(1), end_at=_future(2), location="BOG",
    )
    e.publish()
    e.mark_ongoing()
    e.finish()
    with pytest.raises(InvalidEventStatusTransitionError):
        e.mark_ongoing()
    with pytest.raises(InvalidEventStatusTransitionError):
        e.finish()
    with pytest.raises(InvalidEventStatusTransitionError):
        e.cancel()

    e2 = Event.create(
        id=str(uuid4()), name="Test", description="", organizer_id=str(uuid4()),
        capacity=10, start_at=_future(1), end_at=_future(2), location="BOG",
    )
    e2.publish()
    e2.cancel()
    with pytest.raises(InvalidEventStatusTransitionError):
        e2.cancel()

    e3 = Event.create(
        id=str(uuid4()), name="Test", description="", organizer_id=str(uuid4()),
        capacity=10, start_at=_future(1), end_at=_future(2), location="BOG",
    )
    with pytest.raises(InvalidEventStatusTransitionError):
        e3.mark_ongoing()
    with pytest.raises(InvalidEventStatusTransitionError):
        e3.finish()


def test_event_not_publishable_zero_capacity():
    now = datetime.now(timezone.utc)
    e = Event.from_persistence(
        id=IdValueObject(str(uuid4())),
        name=EventName("Test"),
        description=EventDescription(""),
        organizer_id=IdValueObject(str(uuid4())),
        capacity=EventCapacity(1),
        confirmed_attendees=0,
        dates=EventDateRange(start_at=now, end_at=now + timedelta(days=1)),
        location="BOG",
        status=EventStatus.DRAFT,
        created_at=now,
        updated_at=now,
    )
    from unittest.mock import patch, PropertyMock
    with patch.object(EventCapacity, 'value', new_callable=PropertyMock, return_value=0):
        with pytest.raises(EventNotPublishableError):
            e.publish()


def test_event_ensure_deletable():
    e = Event.create(
        id=str(uuid4()), name="Test", description="", organizer_id=str(uuid4()),
        capacity=10, start_at=_future(1), end_at=_future(2), location="BOG",
    )
    e.publish()
    with pytest.raises(EventNotDeletableError):
        e.ensure_deletable()
    e.cancel()
    e.ensure_deletable()


def test_event_change_capacity_below_confirmed():
    e = Event.create(
        id=str(uuid4()), name="Test", description="", organizer_id=str(uuid4()),
        capacity=10, start_at=_future(1), end_at=_future(2), location="BOG",
    )
    e.publish()
    e.confirmed_attendees = 5
    with pytest.raises(EventCapacityBelowConfirmedError):
        e.change_capacity(3)


def test_event_reserve_spot_not_published():
    e = Event.create(
        id=str(uuid4()), name="Test", description="", organizer_id=str(uuid4()),
        capacity=10, start_at=_future(1), end_at=_future(2), location="BOG",
    )
    with pytest.raises(EventNotPublishedError):
        e.reserve_spot()


def test_event_reserve_spot_full():
    e = Event.create(
        id=str(uuid4()), name="Test", description="", organizer_id=str(uuid4()),
        capacity=1, start_at=_future(1), end_at=_future(2), location="BOG",
    )
    e.publish()
    e.confirmed_attendees = 1
    with pytest.raises(EventFullError):
        e.reserve_spot()


def test_event_release_spot_zero():
    e = Event.create(
        id=str(uuid4()), name="Test", description="", organizer_id=str(uuid4()),
        capacity=1, start_at=_future(1), end_at=_future(2), location="BOG",
    )
    e.publish()
    e.release_spot()
    assert e.confirmed_attendees == 0


def test_event_update_details_and_reschedule():
    e = Event.create(
        id=str(uuid4()), name="Test", description="", organizer_id=str(uuid4()),
        capacity=10, start_at=_future(1), end_at=_future(2), location="BOG",
    )
    e.update_details(name="Updated", description="New", location="MDE")
    assert e.name.value == "Updated"
    assert e.location == "MDE"

    new_start = _future(3)
    new_end = _future(4)
    e.reschedule(start_at=new_start, end_at=new_end)
    assert e.dates.start_at == new_start


def test_event_update_details_invalid():
    e = Event.create(
        id=str(uuid4()), name="Test", description="", organizer_id=str(uuid4()),
        capacity=10, start_at=_future(1), end_at=_future(2), location="BOG",
    )
    with pytest.raises(DomainValidationError) as exc:
        e.update_details(name="ab")
    assert "name" in exc.value.errors

    with pytest.raises(DomainValidationError) as exc:
        e.reschedule(start_at=_future(2), end_at=_future(1))
    assert "dates" in exc.value.errors


def test_event_capacity_validation():
    EventCapacity(10)
    with pytest.raises(InvalidArgumentError):
        EventCapacity(0)
    with pytest.raises(InvalidArgumentError):
        EventCapacity("bad")
    with pytest.raises(InvalidArgumentError):
        EventCapacity(2_000_000)
    with pytest.raises(InvalidArgumentError):
        EventCapacity(True)


def test_event_date_range_validation():
    now = datetime.now(timezone.utc)
    EventDateRange(start_at=now, end_at=now + timedelta(days=1))
    with pytest.raises(InvalidArgumentError):
        EventDateRange(start_at=now, end_at=now)
    with pytest.raises(InvalidArgumentError):
        EventDateRange(start_at="bad", end_at=now)

    a = EventDateRange(start_at=now, end_at=now + timedelta(days=2))
    b = EventDateRange(start_at=now + timedelta(days=1), end_at=now + timedelta(days=3))
    assert a.overlaps(b)
    assert not a.contains(b)
    c = EventDateRange(start_at=now, end_at=now + timedelta(days=1))
    assert a.contains(c)


def test_event_description_validation():
    EventDescription("valid")
    with pytest.raises(InvalidArgumentError):
        EventDescription("x" * 5001)
    with pytest.raises(InvalidArgumentError):
        EventDescription(123)  # type: ignore[arg-type]


def test_event_name_validation():
    EventName("Valid")
    with pytest.raises(InvalidArgumentError):
        EventName("ab")
    with pytest.raises(InvalidArgumentError):
        EventName("x" * 201)
    with pytest.raises(InvalidArgumentError):
        EventName(123)  # type: ignore[arg-type]
    n = EventName("  Hello  ")
    assert n.value == "Hello"


def test_event_errors():
    err = EventNotFoundError("e1")
    assert err.event_id == "e1"
    assert "e1" in str(err)

    err2 = InvalidEventStatusTransitionError("draft", "finished")
    assert err2.current == "draft"
    assert err2.target == "finished"

    err3 = EventNotPublishableError("bad")
    assert err3.reason == "bad"

    err4 = EventNotDeletableError("ongoing")
    assert err4.status == "ongoing"

    err5 = EventCapacityBelowConfirmedError(5, 10)
    assert err5.requested == 5
    assert err5.confirmed == 10

    err6 = EventFullError("e2")
    assert err6.event_id == "e2"

    err7 = EventNotPublishedError("e3", "draft")
    assert err7.event_id == "e3"
    assert err7.status == "draft"
