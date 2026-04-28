from abc import ABC, abstractmethod
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection


class MongoRepository(ABC):
    def __init__(self, client: MongoClient) -> None:
        self._client = client

    @abstractmethod
    def _module_name(self) -> str:
        pass

    @abstractmethod
    def _collection_name(self) -> str:
        pass

    def _collection(self) -> Collection[Any]:
        db = self._client.get_database()
        return db[self._collection_name()]

    def _persist(self, id: str, document: dict) -> None:
        self._collection().replace_one(
            {"_id": id},
            document,
            upsert=True,
        )
