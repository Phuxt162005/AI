"""Role Based Access Control."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Role:
    """Represent an RBAC role."""

    name: str
    permissions: set[str] = field(default_factory=set)

class RBAC:
    """Simple role and permission manager."""

    def __init__(self) -> None:
        self._roles: dict[str, Role] = {}
        self._user_roles: dict[str, set[str]] = {}

    def add_role(
        self,
        name: str,
        permissions: set[str] | None = None,
    ) -> None:
        """Register or replace a role."""

        name = name.strip()
        if not name:
            raise ValueError("role name must not be empty")

        self._roles[name] = Role(
            name=name,
            permissions=set(permissions or set()),
        )

    def assign_role(
        self,
        user_id: str,
        role_name: str,
    ) -> None:
        """Assign a role to a user."""

        if role_name not in self._roles:
            raise KeyError(f"Unknown role: {role_name}")

        self._user_roles.setdefault(user_id, set()).add(role_name)

    def revoke_role(
        self,
        user_id: str,
        role_name: str,
    ) -> None:
        """Revoke a role from a user."""

        self._user_roles.get(user_id, set()).discard(role_name)

    def has_permission(
        self,
        user_id: str,
        permission: str,
    ) -> bool:
        """Check whether a user has a permission."""

        for role_name in self._user_roles.get(user_id, set()):
            role = self._roles.get(role_name)

            if role and permission in role.permissions:
                return True

        return False