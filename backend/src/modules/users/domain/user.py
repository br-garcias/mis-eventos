from dataclasses import dataclass
from datetime import datetime, timezone
from modules.shared.domain.aggregate_root import AggregateRoot
from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.shared.domain.value_object.bool_value_object import BoolValueObject
from modules.shared.domain.domain_validation_error import DomainValidationError
from modules.shared.domain.value_object.invalid_argument_error import InvalidArgumentError
from modules.shared.domain.security.password_hasher import PasswordHasher
from .user_email import UserEmail
from .user_name import UserName
from .user_password import UserPassword

@dataclass
class User(AggregateRoot):
    id: IdValueObject
    name: UserName
    email: UserEmail
    password: UserPassword
    is_active: BoolValueObject
    role_id: IdValueObject
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        id: str,
        name: str,
        email: str,
        password_hash: str,
        role_id: str,
        is_active: bool = True,
    ) -> "User":
        errors = {}

        try:
            user_id = IdValueObject(id)
        except InvalidArgumentError as e:
            errors["id"] = [str(e)]

        try:
            user_name = UserName(name)
        except InvalidArgumentError as e:
            errors["name"] = [str(e)]

        try:
            user_email = UserEmail(email)
        except InvalidArgumentError as e:
            errors["email"] = [str(e)]

        try:
            user_password = UserPassword.from_hash(password_hash)
        except InvalidArgumentError as e:
            errors["password"] = [str(e)]

        try:
            user_role_id = IdValueObject(role_id)
        except InvalidArgumentError as e:
            errors["role_id"] = [str(e)]

        try:
            user_is_active = BoolValueObject(is_active)
        except InvalidArgumentError as e:
            errors["is_active"] = [str(e)]

        if errors:
            raise DomainValidationError(errors)

        now = datetime.now(timezone.utc)
        return cls(
            id=user_id,
            name=user_name,
            email=user_email,
            password=user_password,
            is_active=user_is_active,
            role_id=user_role_id,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        *,
        name: str | None = None,
        email: str | None = None,
        role_id: str | None = None,
    ) -> None:
        candidates = {}
        if name is not None:
            candidates["name"] = (UserName, name)
        if email is not None:
            candidates["email"] = (UserEmail, email)
        if role_id is not None:
            candidates["role_id"] = (IdValueObject, role_id)

        values, errors = self._build_value_objects(candidates)
        if errors:
            raise DomainValidationError(errors)
        for field, vo in values.items():
            setattr(self, field, vo)

    def change_password(self, plain_password: str, hasher: PasswordHasher) -> None:
        try:
            self.password = UserPassword.from_plain(plain_password, hasher)
        except InvalidArgumentError as e:
            raise DomainValidationError({"password": [str(e)]})

    def toggle(self) -> None:
        self.is_active = BoolValueObject(not self.is_active.value)

    @staticmethod
    def _build_value_objects(fields: dict) -> tuple[dict, dict[str, list[str]]]:
        values: dict = {}
        errors: dict[str, list[str]] = {}
        for field, (vo_cls, raw) in fields.items():
            try:
                values[field] = vo_cls(raw)
            except InvalidArgumentError as e:
                errors[field] = [str(e)]
        return values, errors
