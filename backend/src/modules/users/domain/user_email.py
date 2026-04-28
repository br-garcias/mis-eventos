import re
from modules.shared.domain.value_object import StringValueObject, InvalidArgumentError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UserEmail(StringValueObject):
    def _ensure_valid(self) -> None:
        if not _EMAIL_RE.match(self.value):
            raise InvalidArgumentError(f"<{self.value}> is not a valid email")
