"""Repository for messages."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from database.access.data_access import DataAccess
from database.access.repository import BaseRepository, EntityMapper


@dataclass
class Message:
    id: int | None
    conversation_id: int
    role: str
    content: str
    created_at: datetime | None = None


def _message_from_row(row: Any) -> Message:
    return Message(
        id=row.get("id"),
        conversation_id=row["conversation_id"],
        role=row["role"],
        content=row["content"],
        created_at=row.get("created_at"),
    )


def _message_to_row(entity: Message) -> dict[str, Any]:
    row = {
        "conversation_id": entity.conversation_id,
        "role": entity.role,
        "content": entity.content,
    }

    if entity.id is not None:
        row["id"] = entity.id

    return row


class MessageRepository(BaseRepository[Message]):
    """Repository for messages."""

    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[Message](
            from_row=_message_from_row,
            to_row=_message_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="messages",
            mapper=mapper,
            primary_key="id",
        )

    def list_by_conversation(
        self,
        conversation_id: int,
    ) -> list[Message]:
        sql = (
            "SELECT * FROM `messages` "
            "WHERE `conversation_id` = %s "
            "ORDER BY `created_at` ASC"
        )

        rows = self.data_access.query(
            sql,
            [conversation_id],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

    def list_recent(
        self,
        conversation_id: int,
        limit: int = 20,
    ) -> list[Message]:
        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        sql = (
            "SELECT * FROM `messages` "
            "WHERE `conversation_id` = %s "
            "ORDER BY `created_at` DESC "
            "LIMIT %s"
        )
        rows = self.data_access.query(
            sql,
            [conversation_id, limit],
        )
        messages = [
            self.mapper.map_from_row(row)
            for row in rows
        ]
        messages.reverse()

        return messages