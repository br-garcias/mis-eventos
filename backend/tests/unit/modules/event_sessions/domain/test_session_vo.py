"""Unit tests for EventSession value objects."""
import pytest

from modules.event_sessions.domain.session_date_range import SessionDateRange
from modules.event_sessions.domain.session_description import SessionDescription
from modules.event_sessions.domain.session_title import SessionTitle
from modules.shared.domain.value_object.invalid_argument_error import InvalidArgumentError


def test_session_title_valid():
    st = SessionTitle("Hello World")
    assert st.value == "Hello World"


def test_session_title_too_short():
    with pytest.raises(InvalidArgumentError):
        SessionTitle("Hi")


def test_session_title_not_string():
    with pytest.raises(InvalidArgumentError):
        SessionTitle(123)  # type: ignore[arg-type]


def test_session_description_valid():
    sd = SessionDescription("Some description")
    assert sd.value == "Some description"


def test_session_description_too_long():
    with pytest.raises(InvalidArgumentError):
        SessionDescription("x" * 5001)


def test_session_date_range_valid():
    from datetime import datetime, timedelta
    start = datetime.now()
    end = start + timedelta(hours=1)
    dr = SessionDateRange(start_at=start, end_at=end)
    assert dr.start_at == start
    assert dr.end_at == end


def test_session_date_range_overlap():
    from datetime import datetime, timedelta
    base = datetime(2025, 1, 1, 10, 0)
    a = SessionDateRange(base, base + timedelta(hours=2))
    b = SessionDateRange(base + timedelta(hours=1), base + timedelta(hours=3))
    assert a.overlaps(b)
    assert b.overlaps(a)


def test_session_date_range_no_overlap():
    from datetime import datetime, timedelta
    base = datetime(2025, 1, 1, 10, 0)
    a = SessionDateRange(base, base + timedelta(hours=1))
    b = SessionDateRange(base + timedelta(hours=2), base + timedelta(hours=3))
    assert not a.overlaps(b)
