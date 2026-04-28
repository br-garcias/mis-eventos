from pymongo import MongoClient

from modules.roles.domain.role import Role
from modules.roles.domain.role_repository import RoleRepository
from modules.shared.infrastructure.persistence.mongo.mongo_repository import MongoRepository


class MongoRoleRepository(RoleRepository, MongoRepository):
    def __init__(self, client: MongoClient) -> None:
        MongoRepository.__init__(self, client)

    def _module_name(self) -> str:
        return "roles"

    def _collection_name(self) -> str:
        return "roles"

    def save(self, role: Role) -> None:
        self._persist(role.id.value, MongoRoleMapper.to_document(role))

    def find_by_name(self, name: str) -> Role | None:
        document = self._collection().find_one({"role": name})
        return MongoRoleMapper.from_document(document) if document else None

    def find_by_id(self, id: str) -> Role | None:
        document = self._collection().find_one({"_id": id})
        return MongoRoleMapper.from_document(document) if document else None


class MongoRoleMapper:
    @staticmethod
    def to_document(role: Role) -> dict:
        return {
            "_id": role.id.value,
            "role": role.name.value,
            "created_at": role.created_at,
            "updated_at": role.updated_at,
        }

    @staticmethod
    def from_document(document: dict) -> Role:
        return Role.create(
            id=document["_id"],
            name=document["role"],
        )
