from __future__ import annotations

import os
import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from modules.roles.domain.role import Role  # noqa: E402
from modules.roles.domain.role_name import RoleName  # noqa: E402
from modules.users.domain.user import User  # noqa: E402


def main() -> None:
    from apps.api.di.roles_di import role_repository
    from apps.api.di.shared_di import password_hasher
    from apps.api.di.users_di import user_repository

    seeded_roles = []
    for name in (RoleName.ADMIN.value, RoleName.ORGANIZER.value, RoleName.ATTENDEE.value):
        existing = role_repository.find_by_name(name)
        if existing is None:
            role = Role.create(id=str(uuid4()), name=name)
            role_repository.save(role)  # type: ignore[attr-defined]
            seeded_roles.append(name)
    print(f"→ roles ensured (new: {seeded_roles or 'none'})")

    users_to_seed = [
        (
            RoleName.ADMIN.value,
            os.getenv("SEED_ADMIN_EMAIL", "admin@demo.com"),
            os.getenv("SEED_ADMIN_PASSWORD", "Admin#12345"),
            "Root Admin",
        ),
        (
            RoleName.ORGANIZER.value,
            os.getenv("SEED_ORGANIZER_EMAIL", "organizer@demo.com"),
            os.getenv("SEED_ORGANIZER_PASSWORD", "Organizer#12345"),
            "Demo Organizer",
        ),
        (
            RoleName.ATTENDEE.value,
            os.getenv("SEED_ATTENDEE_EMAIL", "attendee@demo.com"),
            os.getenv("SEED_ATTENDEE_PASSWORD", "Attendee#12345"),
            "Demo Attendee",
        ),
    ]

    for role_name, email, password, name in users_to_seed:
        if user_repository.find_by_email(email) is None:
            role = role_repository.find_by_name(role_name)
            assert role is not None, f"{role_name} role missing after seeding"
            user = User.create(
                id=str(uuid4()),
                name=name,
                email=email,
                password_hash=password_hasher.hash(password),
                role_id=role.id.value,
            )
            user_repository.save(user)
            print(f"→ {role_name} user seeded: {email} / {password}")
        else:
            print(f"→ {role_name} user already present: {email}")

    print("✓ seed complete")


if __name__ == "__main__":
    main()
