from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class UserView:
    id: str
    name: str
    email: str

    def to_primitive(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
        }

    @classmethod
    def from_primitive(cls, d: dict[str, Any]) -> "UserView":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            email=d.get("email", ""),
        )


@dataclass(frozen=True)
class MyRegistrationView:
    id: str
    event: dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime

    def to_primitive(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "event": self.event,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_primitive(cls, d: dict[str, Any]) -> "MyRegistrationView":
        return cls(
            id=d["id"],
            event=d.get("event", {}),
            status=d["status"],
            created_at=datetime.fromisoformat(d["created_at"]),
            updated_at=datetime.fromisoformat(d["updated_at"]),
        )


@dataclass(frozen=True)
class EventAttendeeView:
    """An event attendee joined with the user details."""
    id: str
    user: UserView
    status: str
    created_at: datetime
    updated_at: datetime

    def to_primitive(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user": self.user.to_primitive(),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_primitive(cls, d: dict[str, Any]) -> "EventAttendeeView":
        return cls(
            id=d["id"],
            user=UserView.from_primitive(d.get("user", {})),
            status=d["status"],
            created_at=datetime.fromisoformat(d["created_at"]),
            updated_at=datetime.fromisoformat(d["updated_at"]),
        )
