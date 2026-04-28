from dataclasses import dataclass
from datetime import datetime, timezone

from modules.shared.domain.aggregate_root import AggregateRoot
from modules.shared.domain.domain_validation_error import DomainValidationError
from modules.shared.domain.value_object.id_value_object import IdValueObject
from modules.shared.domain.value_object.invalid_argument_error import InvalidArgumentError


@dataclass
class Session(AggregateRoot):
    id: IdValueObject
    user_id: IdValueObject
    user_role_id: IdValueObject
    user_role: str
    refresh_token_hash: str
    ip_address: str
    expires_at: datetime
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        id: str,
        user_id: str,
        user_role_id: str,
        user_role: str,
        refresh_token_hash: str,
        ip_address: str,
        expires_at: datetime,
        created_at: datetime | None = None,
    ) -> "Session":
        errors: dict[str, list[str]] = {}

        try:
            session_id = IdValueObject(id)
        except InvalidArgumentError as e:
            errors["id"] = [str(e)]

        try:
            uid = IdValueObject(user_id)
        except InvalidArgumentError as e:
            errors["user_id"] = [str(e)]

        try:
            rid = IdValueObject(user_role_id)
        except InvalidArgumentError as e:
            errors["user_role_id"] = [str(e)]

        if not isinstance(user_role, str) or not user_role:
            errors["user_role"] = ["User role must be a non-empty string"]

        if not isinstance(refresh_token_hash, str) or not refresh_token_hash:
            errors["refresh_token_hash"] = ["Refresh token hash must be a non-empty string"]

        if not isinstance(ip_address, str):
            errors["ip_address"] = ["IP address must be a string"]

        if not isinstance(expires_at, datetime):
            errors["expires_at"] = ["Expires at must be a datetime"]

        if errors:
            raise DomainValidationError(errors)

        now = created_at or datetime.now(timezone.utc)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        return cls(
            id=session_id,
            user_id=uid,
            user_role_id=rid,
            user_role=user_role,
            refresh_token_hash=refresh_token_hash,
            ip_address=ip_address,
            expires_at=expires_at,
            created_at=now,
        )

    def is_expired(self) -> bool:
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return now > expires

    def ttl_seconds(self) -> int:
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return max(0, int((expires - now).total_seconds()))
