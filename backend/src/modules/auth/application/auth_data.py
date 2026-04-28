from dataclasses import dataclass

from modules.shared.domain.security.token_service import TokenClaims


@dataclass(frozen=True)
class AuthData:
    session_id: str
    user_id: str
    role: str
    role_id: str
    token_id: str

    @classmethod
    def from_claims(cls, claims: TokenClaims) -> "AuthData":
        return cls(
            session_id=claims.session_id,
            user_id=claims.user_id,
            role=claims.role,
            role_id=claims.role_id,
            token_id=claims.token_id,
        )
