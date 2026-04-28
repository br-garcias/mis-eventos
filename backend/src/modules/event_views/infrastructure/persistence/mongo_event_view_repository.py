from __future__ import annotations

from datetime import datetime, timezone

from pymongo import MongoClient

from modules.event_views.domain.event_view_repository import EventViewRepository
from modules.event_views.domain.event_view_dto import (
    EventDetailView,
    EventSessionSummaryView,
    EventSummaryView,
    OrganizerView,
    Page,
)
from modules.shared.infrastructure.persistence.mongo.mongo_repository import MongoRepository


class MongoEventViewRepository(EventViewRepository, MongoRepository):
    def __init__(self, client: MongoClient) -> None:
        MongoRepository.__init__(self, client)

    def _module_name(self) -> str:
        return "event_views"

    def _collection_name(self) -> str:
        return "events"

    def find_by_organizer(
        self,
        organizer_id: str,
        q: str | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> Page[EventSummaryView]:
        query: dict = {"organizer_id": organizer_id}
        if q:
            query["name"] = {"$regex": q, "$options": "i"}
        if status:
            query["status"] = status

        coll = self._collection()
        total = coll.count_documents(query)
        skip = (max(page, 1) - 1) * max(size, 1)
        limit = max(size, 1)

        pipeline = [
            {"$match": query},
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "organizer_id",
                    "foreignField": "_id",
                    "as": "organizer_doc",
                }
            },
            {"$unwind": {"path": "$organizer_doc", "preserveNullAndEmptyArrays": True}},
        ]

        db = self._client.get_database()
        cursor = db["events"].aggregate(pipeline)

        items = [self._to_summary(doc, False) for doc in cursor]
        return Page(items=items, total=total, page=page, size=size)

    def invalidate_cache(self) -> None:
        pass

    _ALLOWED_SORTS = {"start_at", "created_at", "name"}

    def search(
        self,
        *,
        q: str | None = None,
        status: str | None = None,
        organizer_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        sort_by: str = "start_at",
        page: int = 1,
        size: int = 20,
        user_id: str | None = None,
    ) -> Page[EventSummaryView]:
        query: dict = {}
        if q:
            query["name"] = {"$regex": q, "$options": "i"}
        if status:
            query["status"] = status
        if organizer_id:
            query["organizer_id"] = organizer_id
        if date_from or date_to:
            query["start_at"] = {}
            if date_from:
                query["start_at"]["$gte"] = date_from
            if date_to:
                query["start_at"]["$lte"] = date_to

        coll = self._collection()
        total = coll.count_documents(query)
        skip = (max(page, 1) - 1) * max(size, 1)
        limit = max(size, 1)

        sort_field = sort_by if sort_by in self._ALLOWED_SORTS else "start_at"

        pipeline = [
            {"$match": query},
            {"$sort": {sort_field: 1}},
            {"$skip": skip},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "organizer_id",
                    "foreignField": "_id",
                    "as": "organizer_doc",
                }
            },
            {"$unwind": {"path": "$organizer_doc", "preserveNullAndEmptyArrays": True}},
        ]

        db = self._client.get_database()
        cursor = db["events"].aggregate(pipeline)

        registered_event_ids = set()
        if user_id:
            registrations = db["registrations"].find({"user_id": user_id})
            registered_event_ids = {r["event_id"] for r in registrations}

        items = [self._to_summary(doc, user_id is not None and doc["_id"] in registered_event_ids) for doc in cursor]
        return Page(items=items, total=total, page=page, size=size)

    def find_by_id(self, id: str, user_id: str | None = None) -> EventDetailView | None:
        document = self._collection().find_one({"_id": id})
        if not document:
            return None

        db = self._client.get_database()

        sessions_cursor = db["event_sessions"].find({"event_id": id})
        sessions = [self._to_session_summary(doc) for doc in sessions_cursor]

        organizer_doc = db["users"].find_one({"_id": document["organizer_id"]})
        organizer = OrganizerView(
            id=organizer_doc["_id"] if organizer_doc else "",
            name=organizer_doc.get("name", "") if organizer_doc else "",
            email=organizer_doc.get("email", "") if organizer_doc else "",
        )

        is_registered = False
        if user_id:
            registration = db["registrations"].find_one({"user_id": user_id, "event_id": id})
            is_registered = registration is not None

        return self._to_detail(document, organizer, sessions, is_registered)

    @staticmethod
    def _to_session_summary(doc: dict) -> EventSessionSummaryView:
        return EventSessionSummaryView(
            id=doc["_id"],
            event_id=doc.get("event_id", ""),
            title=doc.get("title", ""),
            description=doc.get("description", ""),
            speaker_name=doc.get("speaker_name", ""),
            speaker_bio=doc.get("speaker_bio", ""),
            start_at=doc.get("start_at"),
            end_at=doc.get("end_at"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
        )

    @staticmethod
    def _to_summary(doc: dict, is_registered: bool = False) -> EventSummaryView:
        cap = doc.get("capacity", 0)
        conf = doc.get("confirmed_attendees", 0)
        organizer_doc = doc.get("organizer_doc") or {}
        organizer = OrganizerView(
            id=organizer_doc.get("_id", ""),
            name=organizer_doc.get("name", ""),
            email=organizer_doc.get("email", ""),
        )
        return EventSummaryView(
            id=doc["_id"],
            name=doc["name"],
            description=doc.get("description") or "",
            organizer=organizer,
            status=doc["status"],
            capacity=cap,
            confirmed_attendees=conf,
            available_spots=max(cap - conf, 0),
            start_at=doc["start_at"],
            end_at=doc["end_at"],
            location=doc.get("location") or "",
            is_registered=is_registered,
        )

    @staticmethod
    def _to_detail(doc: dict, organizer: OrganizerView, sessions: list[EventSessionSummaryView], is_registered: bool = False) -> EventDetailView:
        cap = doc.get("capacity", 0)
        conf = doc.get("confirmed_attendees", 0)
        return EventDetailView(
            id=doc["_id"],
            name=doc["name"],
            description=doc.get("description") or "",
            organizer=organizer,
            status=doc["status"],
            capacity=cap,
            confirmed_attendees=conf,
            available_spots=max(cap - conf, 0),
            start_at=doc["start_at"],
            end_at=doc["end_at"],
            location=doc.get("location") or "",
            sessions=sessions,
            created_at=doc.get("created_at") or datetime.now(timezone.utc),
            updated_at=doc.get("updated_at") or datetime.now(timezone.utc),
            is_registered=is_registered,
        )
