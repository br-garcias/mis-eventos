from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RoleView:
    id: str
    name: str

    def to_primitive(self) -> dict[str, Any]:
        return {"id": self.id, "role": self.name}

    @classmethod
    def from_primitive(cls, d: dict[str, Any]) -> "RoleView":
        return cls(id=d["id"], name=d["role"])


@dataclass(frozen=True)
class UserSummaryView:
    id: str
    name: str
    email: str
    is_active: bool
    created_at: str
    updated_at: str
    role: RoleView

    def to_primitive(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "role": self.role.to_primitive(),
        }

    @classmethod
    def from_primitive(cls, d: dict[str, Any]) -> "UserSummaryView":
        return cls(
            id=d["id"],
            name=d["name"],
            email=d["email"],
            is_active=d["is_active"],
            created_at=d["created_at"],
            updated_at=d["updated_at"],
            role=RoleView.from_primitive(d["role"]),
        )


@dataclass(frozen=True)
class UserDetailView:
    id: str
    name: str
    email: str
    is_active: bool
    created_at: str
    updated_at: str
    role: RoleView

    def to_primitive(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "role": self.role.to_primitive(),
        }

    @classmethod
    def from_primitive(cls, d: dict[str, Any]) -> "UserDetailView":
        return cls(
            id=d["id"],
            name=d["name"],
            email=d["email"],
            is_active=d["is_active"],
            created_at=d["created_at"],
            updated_at=d["updated_at"],
            role=RoleView.from_primitive(d["role"]),
        )
