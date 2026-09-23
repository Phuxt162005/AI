"""Retention and deletion policies."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

@dataclass(frozen=True)
class RetentionPolicy:
    """Define how long managed data should be retained."""

    retention_days: int
    allow_deletion: bool = True
    soft_delete: bool = True

    def __post_init__(self) -> None:
        if self.retention_days < 0:
            raise ValueError("retention_days must be >= 0")

class RetentionManager:
    """Apply retention and deletion decisions."""

    def __init__(self, policy: RetentionPolicy) -> None:
        self.policy = policy

    def is_expired(
        self,
        created_at: datetime,
        now: datetime | None = None,
    ) -> bool:
        """Return whether an item exceeded the retention period."""

        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        current_time = now or datetime.now(timezone.utc)
        deadline = created_at + timedelta(days=self.policy.retention_days)

        return current_time >= deadline

    def can_delete(self, created_at: datetime) -> bool:
        """Return whether an item may be deleted."""

        return (
            self.policy.allow_deletion
            and self.is_expired(created_at)
        )

    def delete(
        self,
        store: dict[str, Any],
        object_id: str,
        created_at: datetime,
    ) -> bool:
        """Delete or soft-delete an item from a dictionary store."""

        if object_id not in store:
            return False

        if not self.can_delete(created_at):
            return False

        if self.policy.soft_delete:
            value = store[object_id]

            if isinstance(value, dict):
                value["deleted"] = True
                value["deleted_at"] = datetime.now(
                    timezone.utc
                )
            else:
                store[object_id] = {
                    "value": value,
                    "deleted": True,
                    "deleted_at": datetime.now(timezone.utc),
                }
        else:
            del store[object_id]

        return True