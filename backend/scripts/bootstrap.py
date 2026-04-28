#!/usr/bin/env python3
from __future__ import annotations

import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main() -> int:
    import os
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

    try:
        import migrate

        log.info("Applying MongoDB indexes ...")
        migrate.main()
    except Exception as exc:
        log.error("Migration failed: %s", exc)
        return 1

    try:
        import seed

        log.info("Seeding roles and admin user ...")
        seed.main()
    except Exception as exc:
        log.error("Seeding failed: %s", exc)
        return 1

    log.info("Bootstrap complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
