from modules.shared.domain.security.password_hasher import PasswordHasher
from modules.shared.domain.value_object import StringValueObject, InvalidArgumentError


class UserPassword(StringValueObject):

    MIN_PLAIN_LENGTH = 8
    MAX_PLAIN_BYTES = 72

    def _ensure_valid(self) -> None:
        if not isinstance(self.value, str) or not self.value:
            raise InvalidArgumentError("Password hash must be a non-empty string")

    @classmethod
    def from_plain(cls, plain: str, hasher: PasswordHasher) -> "UserPassword":
        cls._ensure_plain_is_safe(plain)
        return cls(hasher.hash(plain))

    @classmethod
    def from_hash(cls, hashed: str) -> "UserPassword":
        return cls(hashed)

    def matches(self, plain: str, hasher: PasswordHasher) -> bool:
        if not isinstance(plain, str) or not plain:
            return False
        if len(plain.encode("utf-8")) > self.MAX_PLAIN_BYTES:
            return False
        return hasher.verify(plain, self.value)

    @classmethod
    def _ensure_plain_is_safe(cls, plain: str) -> None:
        if not isinstance(plain, str):
            raise InvalidArgumentError("Password must be a string")
        if len(plain) < cls.MIN_PLAIN_LENGTH:
            raise InvalidArgumentError(
                f"Password must be at least {cls.MIN_PLAIN_LENGTH} characters"
            )
        if len(plain.encode("utf-8")) > cls.MAX_PLAIN_BYTES:
            raise InvalidArgumentError(
                f"Password must be at most {cls.MAX_PLAIN_BYTES} bytes"
            )
        if "\x00" in plain:
            raise InvalidArgumentError("Password must not contain null bytes")
        if plain != plain.strip():
            raise InvalidArgumentError("Password must not have leading or trailing whitespace")
