from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Generic, TypeVar


@dataclass(frozen=True)
class OrganizerView:
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
    def from_primitive(cls, d: dict[str, Any]) -> "OrganizerView":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            email=d.get("email", ""),
        )


@dataclass(frozen=True)
class EventSessionSummaryView:
    id: str
    event_id: str
    title: str
    description: str
    speaker_name: str
    speaker_bio: str
    start_at: datetime
    end_at: datetime
    created_at: datetime
    updated_at: datetime

    def to_primitive(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "event_id": self.event_id,
            "title": self.title,
            "description": self.description,
            "speaker_name": self.speaker_name,
            "speaker_bio": self.speaker_bio,
            "start_at": self.start_at.isoformat(),
            "end_at": self.end_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_primitive(cls, d: dict[str, Any]) -> "EventSessionSummaryView":
        return cls(
            id=d.get("id", ""),
            event_id=d.get("event_id", ""),
            title=d.get("title", ""),
            description=d.get("description", ""),
            speaker_name=d.get("speaker_name", ""),
            speaker_bio=d.get("speaker_bio", ""),
            start_at=datetime.fromisoformat(d["start_at"]) if d.get("start_at") else datetime.now(),
            end_at=datetime.fromisoformat(d["end_at"]) if d.get("end_at") else datetime.now(),
            created_at=datetime.fromisoformat(d["created_at"]) if d.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(d["updated_at"]) if d.get("updated_at") else datetime.now(),
        )


@dataclass(frozen=True)
class EventSummaryView:
    id: str
    name: str
    description: str
    organizer: OrganizerView
    status: str
    capacity: int
    confirmed_attendees: int
    available_spots: int
    start_at: datetime
    end_at: datetime
    location: str
    is_registered: bool = False

    def to_primitive(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "organizer": self.organizer.to_primitive(),
            "status": self.status,
            "capacity": self.capacity,
            "confirmed_attendees": self.confirmed_attendees,
            "available_spots": self.available_spots,
            "start_at": self.start_at.isoformat(),
            "end_at": self.end_at.isoformat(),
            "location": self.location,
            "is_registered": self.is_registered,
        }

    @classmethod
    def from_primitive(cls, d: dict[str, Any]) -> EventSummaryView:
        return cls(
            id=d["id"],
            name=d["name"],
            description=d.get("description", ""),
            organizer=OrganizerView.from_primitive(d.get("organizer", {})),
            status=d["status"],
            capacity=d["capacity"],
            confirmed_attendees=d["confirmed_attendees"],
            available_spots=d["available_spots"],
            start_at=datetime.fromisoformat(d["start_at"]),
            end_at=datetime.fromisoformat(d["end_at"]),
            location=d["location"],
            is_registered=d.get("is_registered", False),
        )


@dataclass(frozen=True)
class EventDetailView:
    id: str
    name: str
    description: str
    organizer: OrganizerView
    status: str
    capacity: int
    confirmed_attendees: int
    available_spots: int
    start_at: datetime
    end_at: datetime
    location: str
    sessions: list[EventSessionSummaryView]
    created_at: datetime
    updated_at: datetime
    is_registered: bool = False

    def to_primitive(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "organizer": self.organizer.to_primitive(),
            "status": self.status,
            "capacity": self.capacity,
            "confirmed_attendees": self.confirmed_attendees,
            "available_spots": self.available_spots,
            "start_at": self.start_at.isoformat(),
            "end_at": self.end_at.isoformat(),
            "location": self.location,
            "sessions": [s.to_primitive() for s in self.sessions],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_registered": self.is_registered,
        }

    @classmethod
    def from_primitive(cls, d: dict[str, Any]) -> EventDetailView:
        return cls(
            id=d["id"],
            name=d["name"],
            description=d["description"],
            organizer=OrganizerView.from_primitive(d.get("organizer", {})),
            status=d["status"],
            capacity=d["capacity"],
            confirmed_attendees=d["confirmed_attendees"],
            available_spots=d["available_spots"],
            start_at=datetime.fromisoformat(d["start_at"]),
            end_at=datetime.fromisoformat(d["end_at"]),
            location=d["location"],
            sessions=[EventSessionSummaryView.from_primitive(s) for s in d.get("sessions", [])],
            created_at=datetime.fromisoformat(d["created_at"]),
            updated_at=datetime.fromisoformat(d["updated_at"]),
            is_registered=d.get("is_registered", False),
        )


T = TypeVar("T")


@dataclass(frozen=True)
class Page(Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int

    def to_primitive(self) -> dict[str, Any]:
        return {
            "items": [item.to_primitive() for item in self.items],
            "total": self.total,
            "page": self.page,
            "size": self.size,
        }

    @classmethod
    def from_primitive(cls, d: dict[str, Any], item_factory: Callable[[dict[str, Any]], T]) -> Page[T]:
        return cls(
            items=[item_factory(item) for item in d["items"]],
            total=d["total"],
            page=d["page"],
            size=d["size"],
        )
