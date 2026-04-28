"""Unit tests for Session aggregate."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from modules.auth.domain.session import Session
from modules.auth.domain.session_not_found_error import SessionNotFoundError
from modules.shared.domain.domain_validation_error import DomainValidationError


def _future(days=1):
    return datetime.now(timezone.utc) + timedelta(days=days)


def test_create_session_success():
    s = Session.create(
        id=str(uuid4()),
        user_id=str(uuid4()),
        user_role_id=str(uuid4()),
        user_role="admin",
        refresh_token_hash="hash123",
        ip_address="127.0.0.1",
        expires_at=_future(1),
    )
    assert s.user_role == "admin"
    assert s.ip_address == "127.0.0.1"


def test_create_session_validates_all_fields():
    with pytest.raises(DomainValidationError) as exc:
        Session.create(
            id="bad-uuid",
            user_id="bad-uuid",
            user_role_id="bad-uuid",
            user_role="",
            refresh_token_hash="",
            ip_address=123,
            expires_at="not-a-datetime",
        )
    assert set(exc.value.errors.keys()) == {"id", "user_id", "user_role_id", "user_role", "refresh_token_hash", "ip_address", "expires_at"}


def test_session_is_expired():
    s = Session.create(
        id=str(uuid4()),
        user_id=str(uuid4()),
        user_role_id=str(uuid4()),
        user_role="admin",
        refresh_token_hash="hash123",
        ip_address="127.0.0.1",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )
    assert s.is_expired()
    assert s.ttl_seconds() == 0


def test_session_not_expired():
    s = Session.create(
        id=str(uuid4()),
        user_id=str(uuid4()),
        user_role_id=str(uuid4()),
        user_role="admin",
        refresh_token_hash="hash123",
        ip_address="127.0.0.1",
        expires_at=_future(1),
    )
    assert not s.is_expired()
    assert s.ttl_seconds() > 0


def test_session_naive_expires_at():
    s = Session.create(
        id=str(uuid4()),
        user_id=str(uuid4()),
        user_role_id=str(uuid4()),
        user_role="admin",
        refresh_token_hash="hash123",
        ip_address="127.0.0.1",
        expires_at=datetime.now() + timedelta(days=1),
    )
    assert not s.is_expired()


def test_session_created_at_override():
    custom = datetime(2025, 1, 1, tzinfo=timezone.utc)
    s = Session.create(
        id=str(uuid4()),
        user_id=str(uuid4()),
        user_role_id=str(uuid4()),
        user_role="admin",
        refresh_token_hash="hash123",
        ip_address="127.0.0.1",
        expires_at=_future(1),
        created_at=custom,
    )
    assert s.created_at == custom


def test_session_ip_address_string():
    s = Session.create(
        id=str(uuid4()),
        user_id=str(uuid4()),
        user_role_id=str(uuid4()),
        user_role="admin",
        refresh_token_hash="hash123",
        ip_address="::1",
        expires_at=_future(1),
    )
    assert s.ip_address == "::1"


def test_session_not_found_error():
    err = SessionNotFoundError("sid-123")
    assert err.session_id == "sid-123"
    assert "sid-123" in str(err)
