from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List

from pymongo import MongoClient

from modules.role_views.domain.role_view_dto import RoleView
from modules.role_views.domain.role_view_repository import RoleViewRepository
from modules.shared.infrastructure.persistence.mongo.mongo_repository import MongoRepository


class MongoRoleViewRepository(RoleViewRepository, MongoRepository):
    def __init__(self, client: MongoClient) -> None:
        MongoRepository.__init__(self, client)

    def _module_name(self) -> str:
        return "role_views"

    def _collection_name(self) -> str:
        return "roles"

    def invalidate_cache(self) -> None:
        pass

    def list_all(self) -> List[RoleView]:
        cursor = self._collection().find().sort("role", 1)
        return [self._to_view(doc) for doc in cursor]

    @staticmethod
    def _to_view(doc: dict[str, Any]) -> RoleView:
        return RoleView(
            id=doc["_id"],
            name=doc.get("role", ""),
            created_at=str(doc.get("created_at", "")),
            updated_at=str(doc.get("updated_at", "")),
        )
