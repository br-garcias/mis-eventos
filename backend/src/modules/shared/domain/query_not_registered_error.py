from .query import Query


class QueryNotRegisteredError(Exception):
    def __init__(self, query: Query) -> None:
        query_class = query.__class__.__name__
        super().__init__(f"The query <{query_class}> has not a registered handler")
        self._query = query

    @property
    def query(self) -> Query:
        return self._query
