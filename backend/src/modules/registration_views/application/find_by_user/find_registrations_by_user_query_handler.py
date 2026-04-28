from typing import List

from modules.registration_views.domain.registration_view_dto import MyRegistrationView
from modules.shared.domain.query_handler import QueryHandler

from .find_registrations_by_user_query import FindRegistrationsByUserQuery
from .registrations_finder_by_user import RegistrationsFinderByUser


class FindRegistrationsByUserQueryHandler(QueryHandler):
    def __init__(self, finder: RegistrationsFinderByUser) -> None:
        self._finder = finder

    def subscribed_to(self):
        return FindRegistrationsByUserQuery

    def handle(self, query: FindRegistrationsByUserQuery) -> List[MyRegistrationView]:
        return self._finder.run(query.user_id)
