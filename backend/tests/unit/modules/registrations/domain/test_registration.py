"""Unit tests for Registration aggregate."""
from uuid import uuid4

import pytest

from modules.registrations.domain.errors import RegistrationClosedError
from modules.registrations.domain.registration import Registration
from modules.registrations.domain.registration_status import RegistrationStatus


def test_create_registration_success():
    r = Registration.create(id=str(uuid4()), event_id=str(uuid4()), user_id=str(uuid4()))
    assert r.status == RegistrationStatus.CONFIRMED


def test_cancel_registration_success():
    r = Registration.create(id=str(uuid4()), event_id=str(uuid4()), user_id=str(uuid4()))
    r.cancel()
    assert r.status == RegistrationStatus.CANCELLED


def test_cancel_already_cancelled_raises():
    r = Registration.create(id=str(uuid4()), event_id=str(uuid4()), user_id=str(uuid4()))
    r.cancel()
    with pytest.raises(RegistrationClosedError):
        r.cancel()
