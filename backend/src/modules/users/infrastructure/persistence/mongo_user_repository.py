from pymongo import MongoClient

from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.shared.infrastructure.persistence.mongo.mongo_repository import MongoRepository
from modules.users.domain.user import User
from modules.users.domain.user_repository import UserRepository


class MongoUserRepository(UserRepository, MongoRepository):
    def __init__(self, client: MongoClient) -> None:
        MongoRepository.__init__(self, client)

    def _module_name(self) -> str:
        return "users"

    def _collection_name(self) -> str:
        return "users"

    def save(self, user: User) -> None:
        self._persist(user.id.value, MongoUserMapper.to_document(user))

    def find_by_id(self, id: IdValueObject) -> User | None:
        document = self._collection().find_one({"_id": id.value})
        return MongoUserMapper.from_document(document) if document else None

    def find_by_email(self, email: str) -> User | None:
        document = self._collection().find_one({"email": email})
        return MongoUserMapper.from_document(document) if document else None


class MongoUserMapper:
    @staticmethod
    def to_document(user: User) -> dict:
        return {
            "_id": user.id.value,
            "name": user.name.value,
            "email": user.email.value,
            "password": user.password.value,
            "role_id": user.role_id.value,
            "is_active": user.is_active.value,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

    @staticmethod
    def from_document(document: dict) -> User:
        return User.create(
            id=document["_id"],
            name=document["name"],
            email=document["email"],
            password_hash=document["password"],
            role_id=document["role_id"],
            is_active=document.get("is_active", True),
        )
