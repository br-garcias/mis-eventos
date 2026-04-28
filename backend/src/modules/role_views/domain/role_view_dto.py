from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RoleView:
    id: str
    name: str
    created_at: str
    updated_at: str

    def to_primitive(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_primitive(cls, d: dict[str, Any]) -> "RoleView":
        return cls(
            id=d["id"],
            name=d["name"],
            created_at=d["created_at"],
            updated_at=d["updated_at"],
        )
