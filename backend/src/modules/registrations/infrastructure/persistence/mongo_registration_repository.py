from __future__ import annotations

from datetime import datetime, timezone

from pymongo import MongoClient

from modules.registrations.domain.registration import Registration
from modules.registrations.domain.registration_repository import RegistrationRepository
from modules.registrations.domain.registration_status import RegistrationStatus
from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.shared.infrastructure.persistence.mongo.mongo_repository import MongoRepository


class MongoRegistrationRepository(RegistrationRepository, MongoRepository):
    def __init__(self, client: MongoClient) -> None:
        MongoRepository.__init__(self, client)

    def _module_name(self) -> str:
        return "registrations"

    def _collection_name(self) -> str:
        return "registrations"

    def save(self, registration: Registration) -> None:
        self._persist(registration.id.value, MongoRegistrationMapper.to_document(registration))

    def find_by_id(self, id: IdValueObject) -> Registration | None:
        document = self._collection().find_one({"_id": id.value})
        return MongoRegistrationMapper.from_document(document) if document else None

    def find_by_event_and_user(
        self, event_id: IdValueObject, user_id: IdValueObject
    ) -> Registration | None:
        document = self._collection().find_one(
            {"event_id": event_id.value, "user_id": user_id.value}
        )
        return MongoRegistrationMapper.from_document(document) if document else None

    def find_by_user(
        self, user_id: IdValueObject, *, status: RegistrationStatus | None = None
    ) -> list[Registration]:
        query: dict = {"user_id": user_id.value}
        if status is not None:
            query["status"] = status.value
        cursor = self._collection().find(query).sort("created_at", -1)
        return [MongoRegistrationMapper.from_document(doc) for doc in cursor]

    def find_by_event(
        self, event_id: IdValueObject, *, status: RegistrationStatus | None = None
    ) -> list[Registration]:
        query: dict = {"event_id": event_id.value}
        if status is not None:
            query["status"] = status.value
        cursor = self._collection().find(query).sort("created_at", -1)
        return [MongoRegistrationMapper.from_document(doc) for doc in cursor]


class MongoRegistrationMapper:
    @staticmethod
    def to_document(registration: Registration) -> dict:
        return {
            "_id": registration.id.value,
            "event_id": registration.event_id.value,
            "user_id": registration.user_id.value,
            "status": registration.status.value,
            "created_at": registration.created_at,
            "updated_at": registration.updated_at,
        }

    @staticmethod
    def from_document(document: dict) -> Registration:
        return Registration(
            id=IdValueObject(document["_id"]),
            event_id=IdValueObject(document["event_id"]),
            user_id=IdValueObject(document["user_id"]),
            status=RegistrationStatus(document["status"]),
            created_at=document.get("created_at") or datetime.now(timezone.utc),
            updated_at=document.get("updated_at") or datetime.now(timezone.utc),
        )
