from modules.auth.application.auth_response import AuthResponse
from modules.auth.application.login.user_authenticator import UserAuthenticator
from modules.roles.domain.role_name import RoleName
from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.users.application.create.user_creator import UserCreator


class AttendeeRegistrar:
    def __init__(
        self,
        user_creator: UserCreator,
        user_authenticator: UserAuthenticator,
    ) -> None:
        self._user_creator = user_creator
        self._user_authenticator = user_authenticator

    def register(
        self,
        *,
        name: str,
        email: str,
        password: str,
        ip_address: str,
    ) -> AuthResponse:
        self._user_creator.run(
            id=IdValueObject.random().value,
            name=name,
            email=email,
            password=password,
            role_name=RoleName.ATTENDEE.value,
        )
        return self._user_authenticator.authenticate(email, password, ip_address)
