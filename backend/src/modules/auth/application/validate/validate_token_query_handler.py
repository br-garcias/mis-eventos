from modules.auth.application.auth_data import AuthData
from modules.shared.domain.query_handler import QueryHandler

from .auth_validator import AuthValidator
from .validate_token_query import ValidateTokenQuery


class ValidateTokenQueryHandler(QueryHandler):
    def __init__(self, validator: AuthValidator) -> None:
        self._validator = validator

    def subscribed_to(self):
        return ValidateTokenQuery

    def handle(self, query: ValidateTokenQuery) -> AuthData:
        return self._validator.validate(query.token)
