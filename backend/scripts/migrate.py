from __future__ import annotations

import sys
from pathlib import Path

# Allow running directly as `python scripts/migrate.py`
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from modules.shared.config import get_settings  # noqa: E402
from modules.shared.infrastructure.persistence.mongo.mongo_client_factory import (  # noqa: E402
    MongoClientFactory,
)
from modules.shared.infrastructure.persistence.mongo.mongo_indexes import apply_indexes  # noqa: E402


# ── Migration steps (append-only; idempotent) ─────────────────────────────────
def _step_0001_indexes(db) -> dict:
    """Ensure all collection indexes exist."""
    return apply_indexes(db)


STEPS = [
    ("0001_indexes", _step_0001_indexes),
]


def main() -> None:
    settings = get_settings().mongo
    client = MongoClientFactory.create_client("migrations", settings.url)
    db_name = settings.url.split("/")[-1].split("?")[0] or "database"
    db = client[db_name]

    print(f"→ Connected to mongo db <{db.name}>")
    for name, step in STEPS:
        print(f"  · running {name} …", end=" ", flush=True)
        result = step(db)
        print("ok" if result is None else f"ok ({result})")
    print("✓ migrations complete")


if __name__ == "__main__":
    main()
