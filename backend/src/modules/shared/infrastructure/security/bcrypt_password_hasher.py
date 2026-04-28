import hashlib

import bcrypt

from modules.shared.domain.security.password_hasher import PasswordHasher

_BCRYPT_MAX_BYTES = 72


class BcryptPasswordHasher(PasswordHasher):
    def hash(self, plain: str) -> str:
        return bcrypt.hashpw(self._prepare(plain), bcrypt.gensalt()).decode()

    def verify(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(self._prepare(plain), hashed.encode())

    @staticmethod
    def _prepare(plain: str) -> bytes:
        data = plain.encode("utf-8")
        if len(data) > _BCRYPT_MAX_BYTES:
            data = hashlib.sha256(data).digest()
        return data
