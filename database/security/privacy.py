"""Privacy and data-isolation policies."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DataScope:
    """Define the owner scope of a data object."""

    owner_id: str
    visibility: str = "private"

    def __post_init__(self) -> None:
        if not self.owner_id.strip():
            raise ValueError("owner_id must not be empty")

        if self.visibility not in {
            "private",
            "shared",
            "system",
        }:
            raise ValueError("invalid visibility")

class PrivacyGuard:
    """Enforce basic ownership and isolation rules."""

    def can_access(
        self,
        requester_id: str,
        scope: DataScope,
    ) -> bool:
        """Return whether requester can access the data."""

        if scope.visibility == "system":
            return True

        if scope.visibility == "private":
            return requester_id == scope.owner_id

        return requester_id == scope.owner_id

    def require_access(
        self,
        requester_id: str,
        scope: DataScope,
    ) -> None:
        """Raise when the requester violates the data scope."""

        if not self.can_access(requester_id, scope):
            raise PermissionError("Data access denied by privacy policy")