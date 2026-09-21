"""Repository for conversations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from database.access.data_access import DataAccess
from database.access.repository import BaseRepository, EntityMapper


@dataclass
class Conversation:
    id: int | None
    user_id: int
    title: str | None = None
    status: str = "active"
    created_at: datetime | None = None
    updated_at: datetime | None = None


def _conversation_from_row(row: Any) -> Conversation:
    return Conversation(
        id=row.get("id"),
        user_id=row["user_id"],
        title=row.get("title"),
        status=row.get("status", "active"),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
    )


def _conversation_to_row(entity: Conversation) -> dict[str, Any]:
    row = {
        "user_id": entity.user_id,
        "title": entity.title,
        "status": entity.status,
    }

    if entity.id is not None:
        row["id"] = entity.id

    return row


class ConversationRepository(BaseRepository[Conversation]):
    """Repository for conversations."""

    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[Conversation](
            from_row=_conversation_from_row,
            to_row=_conversation_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="conversations",
            mapper=mapper,
            primary_key="id",
        )

    def list_by_user(self, user_id: int) -> list[Conversation]:
        sql = (
            "SELECT * FROM `conversations` "
            "WHERE `user_id` = %s "
            "ORDER BY `created_at` DESC"
        )

        rows = self.data_access.query(sql, [user_id])

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

    def list_active_by_user(self, user_id: int) -> list[Conversation]:
        sql = (
            "SELECT * FROM `conversations` "
            "WHERE `user_id` = %s "
            "AND `status` = %s "
            "ORDER BY `created_at` DESC"
        )

        rows = self.data_access.query(
            sql,
            [user_id, "active"],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]