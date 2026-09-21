"""Repository for Memory data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from database.access.data_access import DataAccess
from database.access.repository import BaseRepository, EntityMapper
from core.memory.memory import (
    MemoryItem,
    MemoryStatus,
    MemoryType,
)

def _memory_from_row(row: Any) -> MemoryItem:
    return MemoryItem(
        memory_id=row.get("memory_id"),
        user_id=row["user_id"],
        memory_type=MemoryType(row["memory_type"]),
        content=row["content"],
        importance=float(row.get("importance", 0.5)),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
        expires_at=row.get("expires_at"),
        status=MemoryStatus(row.get("status", "active")),
    )


def _memory_to_row(entity: MemoryItem) -> dict[str, Any]:
    row = {
        "user_id": entity.user_id,
        "memory_type": entity.memory_type.value,
        "content": entity.content,
        "importance": entity.importance,
        "expires_at": entity.expires_at,
        "status": entity.status.value,
    }
    if entity.memory_id is not None:
        row["memory_id"] = entity.memory_id

    return row

class MemoryRepository(BaseRepository[MemoryItem]):
    """Repository for MemoryItem."""

    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[MemoryItem](
            from_row=_memory_from_row,
            to_row=_memory_to_row,
        )
        super().__init__(
            data_access=data_access,
            table_name="memories",
            mapper=mapper,
            primary_key="memory_id",
        )
        
    def get_for_user(
        self,
        memory_id: int,
        user_id: int,
    ) -> MemoryItem | None:
        """Retrieve an active memory belonging to a specific user."""

        if memory_id <= 0:
            raise ValueError("memory_id must be greater than zero")

        if user_id <= 0:
            raise ValueError("user_id must be greater than zero")

        sql = (
            "SELECT * FROM `memories` "
            "WHERE `memory_id` = %s "
            "AND `user_id` = %s "
            "AND `status` = %s "
            "AND (`expires_at` IS NULL OR `expires_at` > CURRENT_TIMESTAMP)"
        )

        row = self.data_access.query_one(
            sql,
            [
                memory_id,
                user_id,
                MemoryStatus.ACTIVE.value,
            ],
        )

        if row is None:
            return None

        return self.mapper.map_from_row(row)

    def list_by_user(
        self,
        user_id: int,
        limit: int = 100,
    ) -> list[MemoryItem]:
        """Return active memories belonging to a user."""

        if user_id <= 0:
            raise ValueError("user_id must be greater than zero")
        if limit <= 0:
            raise ValueError("limit must be greater than zero")
        sql = (
            "SELECT * FROM `memories` "
            "WHERE `user_id` = %s "
            "AND `status` = %s "
            "AND (`expires_at` IS NULL OR `expires_at` > CURRENT_TIMESTAMP) "
            "ORDER BY `updated_at` DESC "
            "LIMIT %s"
        )
        rows = self.data_access.query(
            sql,
            [user_id, MemoryStatus.ACTIVE.value, limit],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

    def list_by_type(
        self,
        user_id: int,
        memory_type: MemoryType,
        limit: int = 100,
    ) -> list[MemoryItem]:
        """Return active memories of one type for a user."""

        if user_id <= 0:
            raise ValueError("user_id must be greater than zero")
        if limit <= 0:
            raise ValueError("limit must be greater than zero")
        sql = (
            "SELECT * FROM `memories` "
            "WHERE `user_id` = %s "
            "AND `memory_type` = %s "
            "AND `status` = %s "
            "AND (`expires_at` IS NULL OR `expires_at` > CURRENT_TIMESTAMP) "
            "ORDER BY `importance` DESC, `updated_at` DESC "
            "LIMIT %s"
        )
        rows = self.data_access.query(
            sql,
            [
                user_id,
                memory_type.value,
                MemoryStatus.ACTIVE.value,
                limit,
            ],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

    def find_by_content(
        self,
        user_id: int,
        content: str,
    ) -> MemoryItem | None:
        """
        Find an active memory with the same content.
        This provides a basic conflict-check foundation.
        Semantic similarity belongs to the later Vector DB phase.
        """

        if user_id <= 0:
            raise ValueError("user_id must be greater than zero")
        if not content.strip():
            raise ValueError("content must not be empty")

        sql = (
            "SELECT * FROM `memories` "
            "WHERE `user_id` = %s "
            "AND `content` = %s "
            "AND `status` = %s "
            "AND (`expires_at` IS NULL OR `expires_at` > CURRENT_TIMESTAMP) "
            "LIMIT 1"
        )

        row = self.data_access.query_one(
            sql,
            [
                user_id,
                content,
                MemoryStatus.ACTIVE.value,
            ],
        )

        if row is None:
            return None
        return self.mapper.map_from_row(row)

    def mark_forgotten(
        self,
        memory_id: int,
        user_id: int,
    ) -> None:
        """
        Mark one memory as forgotten.
        user_id is required to preserve memory isolation.
        """

        sql = (
            "UPDATE `memories` "
            "SET `status` = %s "
            "WHERE `memory_id` = %s "
            "AND `user_id` = %s"
        )
        self.data_access.execute(
            sql,
            [
                MemoryStatus.FORGOTTEN.value,
                memory_id,
                user_id,
            ],
        )

    def mark_expired(
        self,
        memory_id: int,
        user_id: int,
    ) -> None:
        """Mark one memory as expired."""

        sql = (
            "UPDATE `memories` "
            "SET `status` = %s "
            "WHERE `memory_id` = %s "
            "AND `user_id` = %s"
        )
        self.data_access.execute(
            sql,
            [
                MemoryStatus.EXPIRED.value,
                memory_id,
                user_id,
            ],
        )

    def expire_due(self) -> None:
        """Mark all expired active memories as expired."""

        sql = (
            "UPDATE `memories` "
            "SET `status` = %s "
            "WHERE `status` = %s "
            "AND `expires_at` IS NOT NULL "
            "AND `expires_at` <= CURRENT_TIMESTAMP"
        )
        self.data_access.execute(
            sql,
            [
                MemoryStatus.EXPIRED.value,
                MemoryStatus.ACTIVE.value,
            ],
        )