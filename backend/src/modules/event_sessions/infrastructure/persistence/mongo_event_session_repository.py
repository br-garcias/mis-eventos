from __future__ import annotations

from datetime import datetime, timezone

from pymongo import MongoClient

from modules.event_sessions.domain.event_session import EventSession
from modules.event_sessions.domain.event_session_repository import EventSessionRepository
from modules.event_sessions.domain.session_date_range import SessionDateRange
from modules.event_sessions.domain.session_description import SessionDescription
from modules.event_sessions.domain.session_title import SessionTitle
from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.shared.infrastructure.persistence.mongo.mongo_repository import MongoRepository


class MongoEventSessionRepository(EventSessionRepository, MongoRepository):
    def __init__(self, client: MongoClient) -> None:
        MongoRepository.__init__(self, client)

    def _module_name(self) -> str:
        return "event_sessions"

    def _collection_name(self) -> str:
        return "event_sessions"

    def save(self, session: EventSession) -> None:
        self._persist(session.id.value, MongoEventSessionMapper.to_document(session))

    def find_by_id(self, id: IdValueObject) -> EventSession | None:
        document = self._collection().find_one({"_id": id.value})
        return MongoEventSessionMapper.from_document(document) if document else None

    def find_by_event(self, event_id: IdValueObject) -> list[EventSession]:
        cursor = self._collection().find({"event_id": event_id.value}).sort("start_at", 1)
        return [MongoEventSessionMapper.from_document(doc) for doc in cursor]

    def find_overlapping(
        self,
        *,
        event_id: IdValueObject,
        start_at: datetime,
        end_at: datetime,
        exclude_id: IdValueObject | None = None,
    ) -> EventSession | None:
        query: dict = {
            "event_id": event_id.value,
            "start_at": {"$lt": end_at},
            "end_at": {"$gt": start_at},
        }
        if exclude_id is not None:
            query["_id"] = {"$ne": exclude_id.value}
        document = self._collection().find_one(query)
        return MongoEventSessionMapper.from_document(document) if document else None

    def delete(self, id: IdValueObject) -> None:
        self._collection().delete_one({"_id": id.value})


class MongoEventSessionMapper:
    @staticmethod
    def to_document(session: EventSession) -> dict:
        return {
            "_id": session.id.value,
            "event_id": session.event_id.value,
            "title": session.title.value,
            "description": session.description.value,
            "speaker_name": session.speaker_name,
            "speaker_bio": session.speaker_bio,
            "start_at": session.time_range.start_at,
            "end_at": session.time_range.end_at,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
        }

    @staticmethod
    def from_document(document: dict) -> EventSession:
        return EventSession(
            id=IdValueObject(document["_id"]),
            event_id=IdValueObject(document["event_id"]),
            title=SessionTitle(document["title"]),
            description=SessionDescription(document.get("description") or ""),
            speaker_name=document.get("speaker_name") or "",
            speaker_bio=document.get("speaker_bio") or "",
            time_range=SessionDateRange(
                start_at=document["start_at"],
                end_at=document["end_at"],
            ),
            created_at=document.get("created_at") or datetime.now(timezone.utc),
            updated_at=document.get("updated_at") or datetime.now(timezone.utc),
        )
