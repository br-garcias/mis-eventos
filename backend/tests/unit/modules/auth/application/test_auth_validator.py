from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from modules.auth.application.validate.auth_validator import AuthValidator
from modules.auth.domain.errors import SessionRevokedError
from modules.auth.domain.session import Session
from modules.shared.domain.security.token_service import TokenClaims
from tests.unit.modules._fakes import FakeSessionRepository, FakeTokenService


SID = str(uuid4())
UID = str(uuid4())
RID = str(uuid4())


def _build():
    token_service = FakeTokenService()
    session_repo = FakeSessionRepository()
    validator = AuthValidator(token_service, session_repo)
    return token_service, session_repo, validator


def _save_session(session_repo: FakeSessionRepository, claims: TokenClaims):
    session = Session.create(
        id=claims.session_id,
        user_id=claims.user_id,
        user_role_id=claims.role_id,
        user_role=claims.role,
        refresh_token_hash="abc",
        ip_address="127.0.0.1",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    session_repo.save(session)


def test_valid_token_with_existing_session_returns_auth_data():
    token_service, session_repo, validator = _build()
    claims = TokenClaims(
        session_id=SID,
        user_id=UID,
        role="admin",
        role_id=RID,
        token_id="tid",
        issued_at=1,
        not_before=1,
        expires_at=9999999999,
    )
    token = token_service.generate(claims)
    _save_session(session_repo, claims)

    result = validator.validate(token)

    assert result.user_id == UID
    assert result.role == "admin"
    assert result.session_id == SID


def test_valid_token_without_session_raises_revoked():
    token_service, _, validator = _build()
    claims = TokenClaims(
        session_id=SID,
        user_id=UID,
        role="admin",
        role_id=RID,
        token_id="tid",
        issued_at=1,
        not_before=1,
        expires_at=9999999999,
    )
    token = token_service.generate(claims)
    # session NOT saved -> revoked

    with pytest.raises(SessionRevokedError):
        validator.validate(token)


def test_bad_token_raises_permission_error():
    _, _, validator = _build()

    with pytest.raises(PermissionError):
        validator.validate("garbage-token")
