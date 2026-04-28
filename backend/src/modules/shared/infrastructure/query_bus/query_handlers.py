from typing import Any, Callable, Dict, List, Type, Union

from modules.shared.domain.query import Query
from modules.shared.domain.query_handler import QueryHandler
from modules.shared.domain.query_not_registered_error import QueryNotRegisteredError
from modules.shared.domain.response import Response


class QueryHandlers:
    def __init__(
        self,
        handlers: Union[List[QueryHandler], Dict[Type[Query], Callable[[Query], Any]]]
    ) -> None:
        if isinstance(handlers, dict):
            self._handlers = dict(handlers)
        else:
            self._handlers = {}
            for handler in handlers:
                self._handlers[handler.subscribed_to()] = handler

    def get(self, query: Query) -> Union[Callable[[Query], Any], QueryHandler]:
        handler = self._handlers.get(type(query))
        if handler is None:
            raise QueryNotRegisteredError(query)
        return handler

    def register(
        self,
        query_class: Type[Query],
        handler: Union[Callable[[Query], Any], QueryHandler]
    ) -> None:
        self._handlers[query_class] = handler
