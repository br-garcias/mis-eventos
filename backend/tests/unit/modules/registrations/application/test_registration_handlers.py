"""Unit tests for Registration command handlers."""
from uuid import uuid4

import pytest

from modules.registrations.application.cancel.cancel_registration_command import CancelRegistrationCommand
from modules.registrations.application.cancel.cancel_registration_command_handler import CancelRegistrationCommandHandler
from modules.registrations.application.cancel.cancel_registration_service import CancelRegistrationService
from modules.registrations.application.cancel_by_event.cancel_registration_by_event_command import CancelRegistrationByEventCommand
from modules.registrations.application.cancel_by_event.cancel_registration_by_event_command_handler import CancelRegistrationByEventCommandHandler
from modules.registrations.application.cancel_by_event.cancel_registration_by_event_service import CancelRegistrationByEventService
from modules.registrations.application.register.register_to_event_command import RegisterToEventCommand
from modules.registrations.application.register.register_to_event_command_handler import RegisterToEventCommandHandler
from modules.registrations.application.register.register_to_event_service import RegisterToEventService
from modules.registrations.domain.errors import RegistrationNotFoundError
from modules.registrations.domain.registration import Registration
from modules.registrations.domain.registration_repository import RegistrationRepository
from modules.registrations.domain.registration_status import RegistrationStatus
from modules.shared.domain.value_object.id_value_object import IdValueObject
from tests.unit.modules._fakes import (
    FakeEventRepository,
    FakeInvalidateCache,
    FakeRegistrationRepository,
    make_event,
    make_user,
)


def test_register_to_event_command_handler():
    event_repo = FakeEventRepository()
    reg_repo = FakeRegistrationRepository()
    cache = FakeInvalidateCache()

    event = make_event(capacity=100)
    event.publish()
    event_repo.save(event)

    service = RegisterToEventService(event_repo, reg_repo, cache)
    handler = RegisterToEventCommandHandler(service)

    rid = str(uuid4())
    uid = str(uuid4())
    cmd = RegisterToEventCommand(
        registration_id=rid,
        event_id=event.id.value,
        user_id=uid,
    )
    handler.handle(cmd)

    assert handler.subscribed_to() == RegisterToEventCommand
    assert reg_repo.find_by_id(IdValueObject(rid)) is not None


def test_cancel_registration_command_handler():
    event_repo = FakeEventRepository()
    reg_repo = FakeRegistrationRepository()
    cache = FakeInvalidateCache()

    event = make_event(capacity=100)
    event.publish()
    event_repo.save(event)
    event.reserve_spot()

    uid = str(uuid4())
    reg = Registration.create(id=str(uuid4()), event_id=event.id.value, user_id=uid)
    reg_repo.save(reg)

    service = CancelRegistrationService(event_repo, reg_repo, cache)
    handler = CancelRegistrationCommandHandler(service)

    cmd = CancelRegistrationCommand(registration_id=reg.id.value, user_id=uid)
    handler.handle(cmd)

    assert handler.subscribed_to() == CancelRegistrationCommand
    updated = reg_repo.find_by_id(reg.id)
    assert updated.status == RegistrationStatus.CANCELLED
    assert cache.calls == 1
    assert event.available_spots == 100


def test_cancel_registration_by_event_command_handler():
    event_repo = FakeEventRepository()
    reg_repo = FakeRegistrationRepository()
    cache = FakeInvalidateCache()

    event = make_event(capacity=100)
    event.publish()
    event_repo.save(event)
    event.reserve_spot()

    uid = str(uuid4())
    reg = Registration.create(id=str(uuid4()), event_id=event.id.value, user_id=uid)
    reg_repo.save(reg)

    cancel_service = CancelRegistrationService(event_repo, reg_repo, cache)
    by_event_service = CancelRegistrationByEventService(reg_repo, cancel_service)
    handler = CancelRegistrationByEventCommandHandler(by_event_service)

    cmd = CancelRegistrationByEventCommand(user_id=uid, event_id=event.id.value)
    handler.handle(cmd)

    assert handler.subscribed_to() == CancelRegistrationByEventCommand
    updated = reg_repo.find_by_id(reg.id)
    assert updated.status == RegistrationStatus.CANCELLED


def test_cancel_registration_by_event_not_found():
    reg_repo = FakeRegistrationRepository()
    cancel_service = CancelRegistrationService(FakeEventRepository(), reg_repo, FakeInvalidateCache())
    by_event_service = CancelRegistrationByEventService(reg_repo, cancel_service)
    handler = CancelRegistrationByEventCommandHandler(by_event_service)

    cmd = CancelRegistrationByEventCommand(user_id=str(uuid4()), event_id=str(uuid4()))
    with pytest.raises(RegistrationNotFoundError):
        handler.handle(cmd)
