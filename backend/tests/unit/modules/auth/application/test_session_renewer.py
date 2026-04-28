from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from modules.auth.application.refresh.session_renewer import SessionRenewer
from modules.auth.application.refresh_token_generator import RefreshTokenGenerator
from modules.auth.application.sessions.session_creator import SessionCreator
from modules.auth.application.sessions.session_revoker import SessionRevoker
from modules.auth.application.token_issuer import TokenIssuer
from modules.auth.domain.errors import InvalidRefreshTokenError, SessionExpiredError
from modules.auth.domain.session import Session
from tests.unit.modules._fakes import FakeSessionRepository, FakeTokenService

SID = str(uuid4())
UID = str(uuid4())
RID = str(uuid4())


def _build_with_active_session(*, expired: bool = False):
    session_repo = FakeSessionRepository()
    token_service = FakeTokenService()
    issuer = TokenIssuer(token_service)
    session_creator = SessionCreator(session_repo)
    session_revoker = SessionRevoker(session_repo)

    refresh = RefreshTokenGenerator.generate()
    expires_at = datetime.now(timezone.utc) + (
        timedelta(seconds=-1) if expired else timedelta(hours=1)
    )
    session = Session.create(
        id=SID,
        user_id=UID,
        user_role_id=RID,
        user_role="admin",
        refresh_token_hash=refresh.hashed,
        ip_address="127.0.0.1",
        expires_at=expires_at,
    )
    session_repo.save(session)

    renewer = SessionRenewer(
        session_repository=session_repo,
        session_revoker=session_revoker,
        session_creator=session_creator,
        token_issuer=issuer,
    )
    return renewer, session_repo, refresh.plain


def test_renew_rotates_session_and_returns_new_tokens():
    renewer, session_repo, refresh_token = _build_with_active_session()

    response = renewer.renew(refresh_token, "10.0.0.1")

    assert response.access_token and response.refresh_token
    # old session must be gone (single-use)
    assert session_repo.find_by_id(SID) is None
    # a brand-new session should exist
    assert len(session_repo._by_id) == 1
    new_session = list(session_repo._by_id.values())[0]
    assert new_session.ip_address == "10.0.0.1"
    assert new_session.user_id.value == UID


def test_renew_rejects_invalid_token():
    renewer, _, _ = _build_with_active_session()
    with pytest.raises(InvalidRefreshTokenError):
        renewer.renew("not-a-real-token", "10.0.0.1")


def test_renew_revokes_expired_session():
    renewer, session_repo, refresh_token = _build_with_active_session(expired=True)

    with pytest.raises(SessionExpiredError):
        renewer.renew(refresh_token, "10.0.0.1")

    assert session_repo.find_by_id(SID) is None
