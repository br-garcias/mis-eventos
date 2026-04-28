from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pymongo import ASCENDING, DESCENDING, TEXT
from pymongo.database import Database


@dataclass(frozen=True)
class IndexSpec:
    keys: list[tuple[str, int | str]]
    name: str
    unique: bool = False
    sparse: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


# ── Per-collection registry ───────────────────────────────────────────────────
INDEXES: dict[str, list[IndexSpec]] = {
    "users": [
        IndexSpec(keys=[("email", ASCENDING)], name="users_email_unique", unique=True),
        IndexSpec(keys=[("role_id", ASCENDING)], name="users_role_id"),
    ],
    "roles": [
        IndexSpec(keys=[("role", ASCENDING)], name="roles_name_unique", unique=True),
    ],
    "events": [
        IndexSpec(keys=[("name", TEXT)], name="events_name_text"),
        IndexSpec(keys=[("name", ASCENDING)], name="events_name_asc"),
        IndexSpec(keys=[("status", ASCENDING), ("start_at", ASCENDING)], name="events_status_start"),
        IndexSpec(keys=[("organizer_id", ASCENDING)], name="events_organizer"),
        IndexSpec(keys=[("created_at", DESCENDING)], name="events_created_desc"),
    ],
    "event_sessions": [
        IndexSpec(keys=[("event_id", ASCENDING), ("start_at", ASCENDING)], name="event_sessions_event_start"),
        IndexSpec(keys=[("event_id", ASCENDING), ("start_at", ASCENDING), ("end_at", ASCENDING)], name="event_sessions_event_start_end"),
    ],
    "registrations": [
        IndexSpec(
            keys=[("event_id", ASCENDING), ("user_id", ASCENDING)],
            name="registrations_event_user_confirmed_unique",
            unique=True,
            extra={"partialFilterExpression": {"status": "confirmed"}},
        ),
        IndexSpec(keys=[("user_id", ASCENDING)], name="registrations_user"),
        IndexSpec(keys=[("event_id", ASCENDING), ("status", ASCENDING)], name="registrations_event_status"),
    ],
}


def apply_indexes(db: Database) -> dict[str, list[str]]:
    report: dict[str, list[str]] = {}
    for collection_name, specs in INDEXES.items():
        created: list[str] = []
        coll = db[collection_name]
        for spec in specs:
            coll.create_index(
                spec.keys,
                name=spec.name,
                unique=spec.unique,
                sparse=spec.sparse,
                **spec.extra,
            )
            created.append(spec.name)
        report[collection_name] = created
    return report
