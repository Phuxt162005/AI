from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from database.access.repository import BaseRepository, EntityMapper

@dataclass
class Message:
    id: int | None
    conversation_id: int
    role: str
    content: str

class MessageMapper(EntityMapper[Message]):
    def from_row(self, row: dict[str, Any]) -> Message:
        return Message(
            id=row.get("id"),
            conversation_id=row["conversation_id"],
            role=row["role"],
            content=row["content"],
        )

    def to_row(self, entity: Message) -> dict[str, Any]:
        return {
            "conversation_id": entity.conversation_id,
            "role": entity.role,
            "content": entity.content,
        }

class MessageRepository(BaseRepository[Message]):
    def __init__(self, data_access):
        super().__init__(
            data_access=data_access,
            table="messages",
            mapper=MessageMapper(),
            primary_key="id",
        )

    def list_by_conversation(self, conversation_id: int) -> list[Message]:
        rows = self.data_access.query(
            """
            SELECT id, conversation_id, role, content
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC
            """,
            (conversation_id,),
        )

        return [self.mapper.from_row(row) for row in rows]

    def list_recent(
        self,
        conversation_id: int,
        limit: int = 20,
    ) -> list[Message]:
        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        rows = self.data_access.query(
            """
            SELECT id, conversation_id, role, content
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (conversation_id, limit),
        )
        rows.reverse()
        return [self.mapper.from_row(row) for row in rows]