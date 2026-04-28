from jose import jwt, JWTError

from modules.shared.domain.security.token_service import TokenService, TokenClaims

_ALGORITHM = "HS256"


class JwtTokenService(TokenService):
    def __init__(self, secret: str, issuer: str) -> None:
        self._secret = secret
        self._issuer = issuer

    def generate(self, claims: TokenClaims) -> str:
        payload = {
            "iss":     self._issuer,
            "sub":     claims.user_id,
            "sid":     claims.session_id,
            "jti":     claims.token_id,
            "iat":     claims.issued_at,
            "nbf":     claims.not_before,
            "exp":     claims.expires_at,
            "role":    claims.role,
            "role_id": claims.role_id,
        }
        return jwt.encode(payload, self._secret, algorithm=_ALGORITHM)

    def verify(self, token: str) -> TokenClaims:
        try:
            data = jwt.decode(
                token,
                self._secret,
                algorithms=[_ALGORITHM],
                issuer=self._issuer,
            )
        except JWTError as e:
            raise ValueError(f"Invalid token: {e}")

        return TokenClaims(
            session_id=data["sid"],
            user_id=data["sub"],
            role=data["role"],
            role_id=data["role_id"],
            token_id=data["jti"],
            issued_at=data["iat"],
            not_before=data["nbf"],
            expires_at=data["exp"],
            issuer=data.get("iss", ""),
        )
