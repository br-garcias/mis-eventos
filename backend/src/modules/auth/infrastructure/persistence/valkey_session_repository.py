from __future__ import annotations

import json
from datetime import datetime, timezone

from modules.auth.domain.session import Session
from modules.auth.domain.session_repository import SessionRepository


class ValkeySessionRepository(SessionRepository):
    def __init__(self, client, *, namespace: str = "auth") -> None:
        self._client = client
        self._ns = namespace

    # ── SessionRepository ─────────────────────────────────────────────────

    def save(self, session: Session) -> None:
        ttl = session.ttl_seconds()
        if ttl <= 0:
            return

        pipe = self._client.pipeline(transaction=True)
        pipe.set(
            self._session_key(session.id.value),
            json.dumps(_SessionMapper.to_dict(session), default=str),
            ex=ttl,
        )
        pipe.set(
            self._refresh_key(session.refresh_token_hash),
            session.id.value,
            ex=ttl,
        )
        pipe.execute()

    def find_by_id(self, session_id: str) -> Session | None:
        raw = self._client.get(self._session_key(session_id))
        return _SessionMapper.from_dict(json.loads(raw)) if raw else None

    def find_by_refresh_hash(self, refresh_token_hash: str) -> Session | None:
        session_id = self._client.get(self._refresh_key(refresh_token_hash))
        if session_id is None:
            return None
        return self.find_by_id(session_id)

    def delete_by_id(self, session_id: str) -> None:
        raw = self._client.get(self._session_key(session_id))
        if raw is None:
            return
        data = json.loads(raw)
        # Atomic: both keys deleted in a single DEL command.
        self._client.delete(
            self._session_key(session_id),
            self._refresh_key(data["refresh_token_hash"]),
        )

    def delete_by_refresh_hash(self, refresh_token_hash: str) -> None:
        session_id = self._client.get(self._refresh_key(refresh_token_hash))
        if session_id is None:
            return
        # Atomic: both keys deleted in a single DEL command.
        self._client.delete(
            self._refresh_key(refresh_token_hash),
            self._session_key(session_id),
        )

    # ── Helpers ────────────────────────────────────────────────────────────

    def _session_key(self, session_id: str) -> str:
        return f"{self._ns}:session:{session_id}"

    def _refresh_key(self, refresh_token_hash: str) -> str:
        return f"{self._ns}:refresh:{refresh_token_hash}"


class _SessionMapper:
    @staticmethod
    def to_dict(session: Session) -> dict:
        return {
            "id": session.id.value,
            "user_id": session.user_id.value,
            "user_role_id": session.user_role_id.value,
            "user_role": session.user_role,
            "refresh_token_hash": session.refresh_token_hash,
            "ip_address": session.ip_address,
            "expires_at": session.expires_at.isoformat(),
            "created_at": session.created_at.isoformat(),
        }

    @staticmethod
    def from_dict(data: dict) -> Session:
        return Session.create(
            id=data["id"],
            user_id=data["user_id"],
            user_role_id=data["user_role_id"],
            user_role=data["user_role"],
            refresh_token_hash=data["refresh_token_hash"],
            ip_address=data["ip_address"],
            expires_at=_parse_dt(data["expires_at"]),
            created_at=_parse_dt(data["created_at"]),
        )


def _parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt
