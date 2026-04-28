from pymongo import MongoClient

from modules.shared.infrastructure.persistence.mongo.mongo_repository import MongoRepository
from modules.user_views.domain.user_view_dto import RoleView, UserDetailView, UserSummaryView
from modules.user_views.domain.user_view_repository import UserViewRepository


class MongoUserViewRepository(UserViewRepository, MongoRepository):
    def __init__(self, client: MongoClient) -> None:
        MongoRepository.__init__(self, client)

    def _module_name(self) -> str:
        return "user_views"

    def _collection_name(self) -> str:
        return "users"

    def invalidate_cache(self) -> None:
        pass

    # ── Port implementation ───────────────────────────────────────────────────
    def search(
        self,
        *,
        email: str | None = None,
        name: str | None = None,
        role_id: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[UserSummaryView], int]:
        match: dict = {}
        if email is not None:
            match["email"] = {"$regex": email, "$options": "i"}
        if name is not None:
            match["name"] = {"$regex": name, "$options": "i"}
        if role_id is not None:
            match["role_id"] = role_id

        total = self._collection().count_documents(match)

        skip = (page - 1) * size
        pipeline: list[dict] = []
        if match:
            pipeline.append({"$match": match})
        pipeline.extend(self._role_lookup_stages())
        pipeline.append({"$skip": skip})
        pipeline.append({"$limit": size})

        items = [self._to_summary(doc) for doc in self._collection().aggregate(pipeline)]
        return items, total

    def find_by_id(self, id: str) -> UserDetailView | None:
        pipeline: list[dict] = [
            {"$match": {"_id": id}},
            *self._role_lookup_stages(),
        ]
        result = list(self._collection().aggregate(pipeline))
        if not result:
            return None
        return self._to_detail(result[0])

    # ── Aggregation helpers ───────────────────────────────────────────────────
    @staticmethod
    def _role_lookup_stages() -> list[dict]:
        return [
            {
                "$lookup": {
                    "from": "roles",
                    "localField": "role_id",
                    "foreignField": "_id",
                    "as": "role_doc",
                },
            },
            {"$unwind": {"path": "$role_doc", "preserveNullAndEmptyArrays": True}},
        ]

    # ── Mappers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _to_role(doc: dict | None) -> RoleView:
        if not doc:
            return RoleView(id="", name="")
        return RoleView(id=doc["_id"], name=doc.get("role", ""))

    @classmethod
    def _to_summary(cls, doc: dict) -> UserSummaryView:
        return UserSummaryView(
            id=doc["_id"],
            name=doc["name"],
            email=doc["email"],
            is_active=doc.get("is_active", True),
            created_at=str(doc.get("created_at", "")),
            updated_at=str(doc.get("updated_at", "")),
            role=cls._to_role(doc.get("role_doc")),
        )

    @classmethod
    def _to_detail(cls, doc: dict) -> UserDetailView:
        return UserDetailView(
            id=doc["_id"],
            name=doc["name"],
            email=doc["email"],
            is_active=doc.get("is_active", True),
            created_at=str(doc.get("created_at", "")),
            updated_at=str(doc.get("updated_at", "")),
            role=cls._to_role(doc.get("role_doc")),
        )
