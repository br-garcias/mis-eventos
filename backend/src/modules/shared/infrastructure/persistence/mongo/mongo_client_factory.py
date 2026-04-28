from pymongo import MongoClient


class MongoClientFactory:
    _clients: dict[str, MongoClient] = {}

    @classmethod
    def create_client(cls, context_name: str, url: str) -> MongoClient:
        client = cls._get_client(context_name)
        if client is None:
            client = cls._create_and_connect_client(url)
            cls._register_client(client, context_name)
        return client

    @classmethod
    def _get_client(cls, context_name: str) -> MongoClient | None:
        return cls._clients.get(context_name)

    @classmethod
    def _create_and_connect_client(cls, url: str) -> MongoClient:
        return MongoClient(url)

    @classmethod
    def _register_client(cls, client: MongoClient, context_name: str) -> None:
        cls._clients[context_name] = client

    @classmethod
    def close_all(cls) -> None:
        for client in cls._clients.values():
            client.close()
        cls._clients.clear()
