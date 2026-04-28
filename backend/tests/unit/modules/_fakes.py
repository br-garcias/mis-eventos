"""Shared in-memory test doubles for unit tests."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from modules.auth.domain.session import Session
from modules.auth.domain.session_repository import SessionRepository
from modules.roles.domain.role import Role
from modules.roles.domain.role_repository import RoleRepository
from modules.shared.domain.security.password_hasher import PasswordHasher
from modules.shared.domain.security.token_service import TokenClaims, TokenService
from modules.events.domain.event import Event
from modules.events.domain.event_repository import EventRepository
from modules.event_sessions.domain.event_session import EventSession
from modules.event_sessions.domain.event_session_repository import EventSessionRepository
from modules.registrations.domain.registration import Registration
from modules.registrations.domain.registration_repository import RegistrationRepository
from modules.registrations.domain.registration_status import RegistrationStatus
from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.users.domain.user import User
from modules.users.domain.user_repository import UserRepository


class FakeInvalidateCache:
    """Shared cache invalidator double tracking call count."""

    def __init__(self) -> None:
        self.calls = 0

    def invalidate_all(self) -> None:
        self.calls += 1


class FakePasswordHasher(PasswordHasher):
    """Reversible 'hash' for tests: prefixes plaintext."""

    PREFIX = "hashed::"

    def hash(self, plain: str) -> str:
        return self.PREFIX + plain

    def verify(self, plain: str, hashed: str) -> bool:
        return hashed == self.PREFIX + plain


class FakeTokenService(TokenService):
    """Encodes claims as a deterministic string. Stores them by token for verify()."""

    def __init__(self) -> None:
        self._store: dict[str, TokenClaims] = {}

    def generate(self, claims: TokenClaims) -> str:
        token = f"tok-{claims.token_id}"
        self._store[token] = claims
        return token

    def verify(self, token: str) -> TokenClaims:
        if token not in self._store:
            raise ValueError("Invalid token")
        return self._store[token]


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self._by_id: dict[str, User] = {}

    def save(self, user: User) -> None:
        self._by_id[user.id.value] = user

    def find_by_id(self, id: IdValueObject) -> Optional[User]:
        return self._by_id.get(id.value)

    def find_by_email(self, email: str) -> Optional[User]:
        return next((u for u in self._by_id.values() if u.email.value == email), None)


class FakeRoleRepository(RoleRepository):
    def __init__(self) -> None:
        self._by_id: dict[str, Role] = {}

    def add(self, role: Role) -> None:
        self._by_id[role.id.value] = role

    def find_by_id(self, id: str) -> Optional[Role]:
        return self._by_id.get(id)

    def find_by_name(self, name: str) -> Optional[Role]:
        return next((r for r in self._by_id.values() if r.name.value == name), None)


class FakeSessionRepository(SessionRepository):
    def __init__(self) -> None:
        self._by_id: dict[str, Session] = {}

    def save(self, session: Session) -> None:
        self._by_id[session.id.value] = session

    def find_by_id(self, session_id: str) -> Optional[Session]:
        return self._by_id.get(session_id)

    def find_by_refresh_hash(self, refresh_token_hash: str) -> Optional[Session]:
        return next(
            (s for s in self._by_id.values() if s.refresh_token_hash == refresh_token_hash),
            None,
        )

    def delete_by_id(self, session_id: str) -> None:
        self._by_id.pop(session_id, None)

    def delete_by_refresh_hash(self, refresh_token_hash: str) -> None:
        session = self.find_by_refresh_hash(refresh_token_hash)
        if session is not None:
            self._by_id.pop(session.id.value, None)


# ── Builders ──────────────────────────────────────────────────────────────────
def make_role(name: str = "admin", id: Optional[str] = None) -> Role:
    return Role.create(id=id or str(uuid4()), name=name)


def make_user(
    *,
    hasher: PasswordHasher,
    email: str = "alice@example.com",
    password: str = "Sup3rSecret!",
    role_id: Optional[str] = None,
    is_active: bool = True,
    id: Optional[str] = None,
    name: str = "Alice",
) -> tuple[User, str]:
    """Returns (user, plain_password) so tests can re-use the password."""
    return (
        User.create(
            id=id or str(uuid4()),
            name=name,
            email=email,
            password_hash=hasher.hash(password),
            role_id=role_id or str(uuid4()),
            is_active=is_active,
        ),
        password,
    )


def make_event(
    *,
    id: Optional[str] = None,
    name: str = "Test Event",
    description: str = "",
    organizer_id: Optional[str] = None,
    capacity: int = 100,
    start_at: Optional[datetime] = None,
    end_at: Optional[datetime] = None,
    location: str = "BOG",
) -> Event:
    from datetime import timedelta, timezone
    now = datetime.now(timezone.utc)
    return Event.create(
        id=id or str(uuid4()),
        name=name,
        description=description,
        organizer_id=organizer_id or str(uuid4()),
        capacity=capacity,
        start_at=start_at or (now + timedelta(days=1)),
        end_at=end_at or (now + timedelta(days=2)),
        location=location,
    )


class FakeEventRepository(EventRepository):
    def __init__(self) -> None:
        self._by_id: dict[str, Event] = {}
        self._reserved: set[str] = set()

    def save(self, event: Event) -> None:
        self._by_id[event.id.value] = event

    def find_by_id(self, id: IdValueObject) -> Optional[Event]:
        return self._by_id.get(id.value)

    def delete(self, id: IdValueObject) -> None:
        self._by_id.pop(id.value, None)

    def reserve_spot(self, id: IdValueObject) -> bool:
        event = self._by_id.get(id.value)
        if event is None or event.status.value != "published" or event.is_full():
            return False
        event.confirmed_attendees += 1
        event._touch()
        self._reserved.add(id.value)
        return True

    def release_spot(self, id: IdValueObject) -> bool:
        event = self._by_id.get(id.value)
        if event is None or event.confirmed_attendees <= 0:
            return False
        event.confirmed_attendees -= 1
        event._touch()
        self._reserved.discard(id.value)
        return True


class FakeEventSessionRepository(EventSessionRepository):
    def __init__(self) -> None:
        self._by_id: dict[str, EventSession] = {}
        self._by_event: dict[str, list[EventSession]] = {}

    def save(self, session: EventSession) -> None:
        self._by_id[session.id.value] = session
        self._by_event.setdefault(session.event_id.value, []).append(session)

    def find_by_id(self, id: IdValueObject) -> EventSession | None:
        return self._by_id.get(id.value)

    def find_by_event(self, event_id: IdValueObject) -> list[EventSession]:
        return list(self._by_event.get(event_id.value, []))

    def find_overlapping(
        self,
        *,
        event_id: IdValueObject,
        start_at,
        end_at,
        exclude_id: IdValueObject | None = None,
    ) -> EventSession | None:
        for s in self._by_event.get(event_id.value, []):
            if exclude_id is not None and s.id.value == exclude_id.value:
                continue
            if s.time_range.overlaps(type(s.time_range)(start_at=start_at, end_at=end_at)):
                return s
        return None

    def delete(self, id: IdValueObject) -> None:
        s = self._by_id.pop(id.value, None)
        if s is not None:
            event_list = self._by_event.get(s.event_id.value, [])
            self._by_event[s.event_id.value] = [es for es in event_list if es.id.value != id.value]


class FakeRegistrationRepository(RegistrationRepository):
    def __init__(self) -> None:
        self._by_id: dict[str, Registration] = {}
        self._save_should_fail: bool = False

    def save(self, registration: Registration) -> None:
        if self._save_should_fail:
            raise RuntimeError("simulated persistence failure")
        self._by_id[registration.id.value] = registration

    def find_by_id(self, id: IdValueObject) -> Optional[Registration]:
        return self._by_id.get(id.value)

    def find_by_event_and_user(
        self, event_id: IdValueObject, user_id: IdValueObject
    ) -> Optional[Registration]:
        return next(
            (
                r
                for r in self._by_id.values()
                if r.event_id.value == event_id.value and r.user_id.value == user_id.value
            ),
            None,
        )

    def find_by_user(
        self, user_id: IdValueObject, *, status: RegistrationStatus | None = None
    ) -> list[Registration]:
        results = [r for r in self._by_id.values() if r.user_id.value == user_id.value]
        if status is not None:
            results = [r for r in results if r.status == status]
        return results

    def find_by_event(
        self, event_id: IdValueObject, *, status: RegistrationStatus | None = None
    ) -> list[Registration]:
        results = [r for r in self._by_id.values() if r.event_id.value == event_id.value]
        if status is not None:
            results = [r for r in results if r.status == status]
        return results
