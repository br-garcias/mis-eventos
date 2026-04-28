"""Unit tests for CancelRegistrationService."""
from uuid import uuid4

import pytest

from modules.registration_views.application.invalidate_cache.invalidate_registration_views_cache import (
    InvalidateRegistrationViewsCache,
)
from modules.registration_views.domain.registration_view_repository import (
    RegistrationViewRepository,
)
from modules.registrations.application.cancel.cancel_registration_service import (
    CancelRegistrationService,
)
from modules.registrations.domain.errors import RegistrationNotFoundError
from modules.registrations.domain.registration import Registration
from tests.unit.modules._fakes import FakeEventRepository, FakeRegistrationRepository, make_event


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
    service = CancelRegistrationService(event_repo, reg_repo, cache_invalidator)
    return event_repo, reg_repo, service


class TestCancelRegistrationService:
    def test_cancel_success(self):
        event_repo, reg_repo, service = _build()
        event = make_event(capacity=10)
        event.publish()
        event.confirmed_attendees = 1
        event_repo.save(event)

        user_id = str(uuid4())
        reg = Registration.create(
            id=str(uuid4()), event_id=event.id.value, user_id=user_id
        )
        reg_repo.save(reg)

        service.run(registration_id=reg.id.value, user_id=user_id)

        assert reg_repo._by_id[reg.id.value].status.value == "cancelled"
        assert event_repo._by_id[event.id.value].confirmed_attendees == 0

    def test_cancel_not_found_raises(self):
        _, _, service = _build()
        with pytest.raises(RegistrationNotFoundError):
            service.run(registration_id=str(uuid4()), user_id=str(uuid4()))

    def test_cancel_wrong_user_raises_not_found(self):
        _, reg_repo, service = _build()
        user_id = str(uuid4())
        reg = Registration.create(id=str(uuid4()), event_id=str(uuid4()), user_id=user_id)
        reg_repo.save(reg)

        with pytest.raises(RegistrationNotFoundError):
            service.run(registration_id=reg.id.value, user_id=str(uuid4()))

    def test_cancel_already_cancelled_is_noop(self):
        event_repo, reg_repo, service = _build()
        event = make_event(capacity=10)
        event.publish()
        event_repo.save(event)

        user_id = str(uuid4())
        reg = Registration.create(
            id=str(uuid4()), event_id=event.id.value, user_id=user_id
        )
        reg.cancel()
        reg_repo.save(reg)

        service.run(registration_id=reg.id.value, user_id=user_id)

        assert event_repo._by_id[event.id.value].confirmed_attendees == 0
        assert reg_repo._by_id[reg.id.value].status.value == "cancelled"
