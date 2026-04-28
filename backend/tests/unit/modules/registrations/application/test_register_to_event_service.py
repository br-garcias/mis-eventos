"""Unit tests for RegisterToEventService."""
from uuid import uuid4

import pytest

from modules.events.domain.errors import EventNotFoundError
from modules.registration_views.application.invalidate_cache.invalidate_registration_views_cache import (
    InvalidateRegistrationViewsCache,
)
from modules.registration_views.domain.registration_view_repository import (
    RegistrationViewRepository,
)
from modules.registrations.application.register.register_to_event_service import (
    RegisterToEventService,
)
from modules.registrations.domain.errors import (
    AlreadyRegisteredError,
    RegistrationClosedError,
)
from modules.shared.domain.value_object.id_value_object import IdValueObject
from tests.unit.modules._fakes import (
    FakeEventRepository,
    FakeRegistrationRepository,
    make_event,
)


class FakeRegistrationViewRepository(RegistrationViewRepository):
    def find_by_user(self, user_id: str):
        return []

    def find_by_event(self, event_id: str):
        return []

    def invalidate_cache(self) -> None:
        pass


def _build():
    event_repo = FakeEventRepository()
    reg_repo = FakeRegistrationRepository()
    cache_invalidator = InvalidateRegistrationViewsCache(FakeRegistrationViewRepository())
    service = RegisterToEventService(event_repo, reg_repo, cache_invalidator)
    return event_repo, reg_repo, service


class TestRegisterToEventService:
    def test_register_success(self):
        event_repo, reg_repo, service = _build()
        event = make_event(capacity=10)
        event.publish()
        event_repo.save(event)

        reg_id = str(uuid4())
        user_id = str(uuid4())
        service.run(registration_id=reg_id, event_id=event.id.value, user_id=user_id)

        saved = reg_repo._by_id[reg_id]
        assert saved.id.value == reg_id
        assert saved.event_id.value == event.id.value
        assert saved.user_id.value == user_id
        assert saved.status.value == "confirmed"
        assert event_repo._by_id[event.id.value].confirmed_attendees == 1

    def test_register_event_not_found_raises(self):
        _, _, service = _build()
        with pytest.raises(EventNotFoundError):
            service.run(registration_id=str(uuid4()), event_id=str(uuid4()), user_id=str(uuid4()))

    def test_register_already_registered_raises(self):
        event_repo, reg_repo, service = _build()
        event = make_event(capacity=10)
        event.publish()
        event_repo.save(event)

        user_id = str(uuid4())
        service.run(registration_id=str(uuid4()), event_id=event.id.value, user_id=user_id)

        with pytest.raises(AlreadyRegisteredError):
            service.run(registration_id=str(uuid4()), event_id=event.id.value, user_id=user_id)

    def test_register_full_event_raises(self):
        event_repo, reg_repo, service = _build()
        event = make_event(capacity=1)
        event.publish()
        event_repo.save(event)

        service.run(registration_id=str(uuid4()), event_id=event.id.value, user_id=str(uuid4()))

        with pytest.raises(RegistrationClosedError):
            service.run(registration_id=str(uuid4()), event_id=event.id.value, user_id=str(uuid4()))

    def test_register_draft_event_raises(self):
        event_repo, _, service = _build()
        event = make_event(capacity=10)
        event_repo.save(event)

        with pytest.raises(RegistrationClosedError):
            service.run(registration_id=str(uuid4()), event_id=event.id.value, user_id=str(uuid4()))

    def test_register_compensates_spot_on_save_failure(self):
        event_repo, reg_repo, service = _build()
        event = make_event(capacity=10)
        event.publish()
        event_repo.save(event)

        reg_repo._save_should_fail = True

        with pytest.raises(RuntimeError, match="simulated persistence failure"):
            service.run(registration_id=str(uuid4()), event_id=event.id.value, user_id=str(uuid4()))

        assert event_repo._by_id[event.id.value].confirmed_attendees == 0
