from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass

_REFRESH_TOKEN_BYTES = 32


@dataclass(frozen=True)
class RefreshToken:
    plain: str
    hashed: str


class RefreshTokenGenerator:
    @staticmethod
    def generate() -> RefreshToken:
        plain = secrets.token_urlsafe(_REFRESH_TOKEN_BYTES)
        return RefreshToken(plain=plain, hashed=RefreshTokenGenerator.hash(plain))

    @staticmethod
    def hash(plain: str) -> str:
        return hashlib.sha256(plain.encode("utf-8")).hexdigest()
