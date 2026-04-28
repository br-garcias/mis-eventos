from modules.auth.application.token_issuer import TokenIssuer
from tests.unit.modules._fakes import FakeTokenService


def test_issues_access_token_with_jti_and_exp():
    service = FakeTokenService()
    issuer = TokenIssuer(service)

    access = issuer.issue_access(session_id="sid", user_id="uid", role="admin", role_id="rid")

    assert access.token_id
    assert access.expires_at > 0


def test_claims_carry_business_fields():
    service = FakeTokenService()
    issuer = TokenIssuer(service)

    access = issuer.issue_access(session_id="sid", user_id="uid", role="admin", role_id="rid")
    claims = service.verify(access.value)

    assert claims.session_id == "sid"
    assert claims.user_id == "uid"
    assert claims.role == "admin"
    assert claims.role_id == "rid"
    assert claims.issued_at == claims.not_before
    assert claims.expires_at > claims.issued_at
