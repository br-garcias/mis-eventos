from __future__ import annotations

from datetime import datetime, timezone

from pymongo import MongoClient, ReturnDocument

from modules.events.domain.event import Event
from modules.events.domain.event_repository import EventRepository
from modules.events.domain.event_status import EventStatus
from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.shared.infrastructure.persistence.mongo.mongo_repository import MongoRepository


class MongoEventRepository(EventRepository, MongoRepository):
    def __init__(self, client: MongoClient) -> None:
        MongoRepository.__init__(self, client)

    def _module_name(self) -> str:
        return "events"

    def _collection_name(self) -> str:
        return "events"

    # ── Write side ────────────────────────────────────────────────────────────
    def save(self, event: Event) -> None:
        self._persist(event.id.value, MongoEventMapper.to_document(event))

    def find_by_id(self, id: IdValueObject) -> Event | None:
        document = self._collection().find_one({"_id": id.value})
        return MongoEventMapper.from_document(document) if document else None

    def delete(self, id: IdValueObject) -> None:
        self._collection().delete_one({"_id": id.value})

    # ── Concurrency-safe spot bookkeeping ─────────────────────────────────────
    def reserve_spot(self, id: IdValueObject) -> bool:
        document = self._collection().find_one_and_update(
            {
                "_id": id.value,
                "status": EventStatus.PUBLISHED.value,
                "$expr": {"$lt": ["$confirmed_attendees", "$capacity"]},
            },
            {"$inc": {"confirmed_attendees": 1}, "$set": {"updated_at": datetime.now(timezone.utc)}},
            return_document=ReturnDocument.AFTER,
        )
        return document is not None

    def release_spot(self, id: IdValueObject) -> bool:
        document = self._collection().find_one_and_update(
            {"_id": id.value, "confirmed_attendees": {"$gt": 0}},
            {"$inc": {"confirmed_attendees": -1}, "$set": {"updated_at": datetime.now(timezone.utc)}},
            return_document=ReturnDocument.AFTER,
        )
        return document is not None


class MongoEventMapper:
    @staticmethod
    def to_document(event: Event) -> dict:
        return {
            "_id":                 event.id.value,
            "name":                event.name.value,
            "description":         event.description.value,
            "organizer_id":        event.organizer_id.value,
            "capacity":            event.capacity.value,
            "confirmed_attendees": event.confirmed_attendees,
            "start_at":            event.dates.start_at,
            "end_at":              event.dates.end_at,
            "location":            event.location,
            "status":              event.status.value,
            "created_at":          event.created_at,
            "updated_at":          event.updated_at,
        }

    @staticmethod
    def from_document(document: dict) -> Event:
        from modules.events.domain.event_capacity import EventCapacity
        from modules.events.domain.event_date_range import EventDateRange
        from modules.events.domain.event_description import EventDescription
        from modules.events.domain.event_name import EventName

        return Event.from_persistence(
            id=IdValueObject(document["_id"]),
            name=EventName(document["name"]),
            description=EventDescription(document.get("description") or ""),
            organizer_id=IdValueObject(document["organizer_id"]),
            capacity=EventCapacity(document["capacity"]),
            confirmed_attendees=document.get("confirmed_attendees", 0),
            dates=EventDateRange(start_at=document["start_at"], end_at=document["end_at"]),
            location=document.get("location") or "",
            status=EventStatus(document["status"]),
            created_at=document.get("created_at") or datetime.now(timezone.utc),
            updated_at=document.get("updated_at") or datetime.now(timezone.utc),
        )
