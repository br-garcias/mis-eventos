from typing import Any, Callable, Dict, Type, Union

from modules.shared.domain.query import Query
from modules.shared.domain.query_bus import QueryBus
from modules.shared.domain.query_handler import QueryHandler
from .query_handlers import QueryHandlers


class InMemoryQueryBus(QueryBus):
    def __init__(
        self,
        handlers: Union[QueryHandlers, Dict[Type[Query], Callable[[Query], Any]]]
    ) -> None:
        if isinstance(handlers, QueryHandlers):
            self._handlers = handlers
        else:
            self._handlers = QueryHandlers(handlers)

    def ask(self, query: Query) -> Any:
        handler = self._handlers.get(query)
        if isinstance(handler, QueryHandler):
            return handler.handle(query)
        return handler(query)
