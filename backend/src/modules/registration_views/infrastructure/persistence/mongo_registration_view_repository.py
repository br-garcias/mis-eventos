from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List

from modules.registration_views.domain.registration_view_repository import (
    RegistrationViewRepository,
)
from modules.registration_views.domain.registration_view_dto import (
    EventAttendeeView,
    MyRegistrationView,
    UserView,
)
from pymongo import MongoClient

from modules.shared.infrastructure.persistence.mongo.mongo_repository import (
    MongoRepository,
)


class MongoRegistrationViewRepository(RegistrationViewRepository, MongoRepository):
    def __init__(self, client: MongoClient) -> None:
        MongoRepository.__init__(self, client)

    def _module_name(self) -> str:
        return "registration_views"

    def _collection_name(self) -> str:
        return "registrations"

    def invalidate_cache(self) -> None:
        pass

    def find_by_user(self, user_id: str) -> List[MyRegistrationView]:
        pipeline: List[dict] = [
            {"$match": {"user_id": user_id}},
            {
                "$lookup": {
                    "from": "events",
                    "localField": "event_id",
                    "foreignField": "_id",
                    "as": "event_doc",
                },
            },
            {"$unwind": {"path": "$event_doc", "preserveNullAndEmptyArrays": True}},
            {"$sort": {"created_at": -1}},
        ]
        return [self._to_my_registration(doc) for doc in self._collection().aggregate(pipeline)]

    def find_by_event(self, event_id: str) -> List[EventAttendeeView]:
        pipeline: List[dict] = [
            {"$match": {"event_id": event_id}},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "_id",
                    "as": "user_doc",
                },
            },
            {"$unwind": {"path": "$user_doc", "preserveNullAndEmptyArrays": True}},
            {"$sort": {"created_at": -1}},
        ]
        return [self._to_event_attendee(doc) for doc in self._collection().aggregate(pipeline)]

    @staticmethod
    def _to_my_registration(doc: dict[str, Any]) -> MyRegistrationView:
        event = doc.get("event_doc") or {}
        event_obj = {
            "id": event.get("_id", ""),
            "name": event.get("name", ""),
            "description": event.get("description", ""),
            "start_at": event.get("start_at").isoformat() if event.get("start_at") else None,
            "end_at": event.get("end_at").isoformat() if event.get("end_at") else None,
            "location": event.get("location", ""),
            "status": event.get("status", ""),
        }
        return MyRegistrationView(
            id=doc["_id"],
            event=event_obj,
            status=doc.get("status") or "",
            created_at=doc.get("created_at") or datetime.now(timezone.utc),
            updated_at=doc.get("updated_at") or datetime.now(timezone.utc),
        )

    @staticmethod
    def _to_event_attendee(doc: dict[str, Any]) -> EventAttendeeView:
        user = doc.get("user_doc") or {}
        return EventAttendeeView(
            id=doc["_id"],
            user=UserView(
                id=str(user.get("_id", "")),
                name=user.get("name") or "",
                email=user.get("email") or "",
            ),
            status=doc.get("status") or "",
            created_at=doc.get("created_at") or datetime.now(timezone.utc),
            updated_at=doc.get("updated_at") or datetime.now(timezone.utc),
        )
