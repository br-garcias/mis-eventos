from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class TokenClaims:

    # Business
    session_id: str   # sid
    user_id: str      # sub
    role: str         # role
    role_id: str      # role_id

    # Standard JWT bookkeeping
    token_id: str     # jti
    issued_at: int    # iat (unix)
    not_before: int   # nbf (unix)
    expires_at: int   # exp (unix)
    issuer: str = ""  # iss (filled on verify; ignored on generate)


class TokenService(ABC):
    @abstractmethod
    def generate(self, claims: TokenClaims) -> str: ...

    @abstractmethod
    def verify(self, token: str) -> TokenClaims: ...
