from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from database.access.repository import BaseRepository, EntityMapper

@dataclass
class Conversation:
    id: int | None
    user_id: int
    title: str | None = None
    status: str = "active"

class ConversationMapper(EntityMapper[Conversation]):
    def from_row(self, row: dict[str, Any]) -> Conversation:
        return Conversation(
            id=row.get("id"),
            user_id=row["user_id"],
            title=row.get("title"),
            status=row.get("status", "active"),
        )

    def to_row(self, entity: Conversation) -> dict[str, Any]:
        return {
            "user_id": entity.user_id,
            "title": entity.title,
            "status": entity.status,
        }

class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, data_access):
        super().__init__(
            data_access=data_access,
            table="conversations",
            mapper=ConversationMapper(),
            primary_key="id",
        )

    def list_by_user(self, user_id: int) -> list[Conversation]:
        rows = self.data_access.query(
            """
            SELECT id, user_id, title, status
            FROM conversations
            WHERE user_id = %s
            ORDER BY created_at ASC
            """,
            (user_id,),
        )

        return [self.mapper.from_row(row) for row in rows]

    def list_active_by_user(self, user_id: int) -> list[Conversation]:
        rows = self.data_access.query(
            """
            SELECT id, user_id, title, status
            FROM conversations
            WHERE user_id = %s
              AND status = %s
            ORDER BY created_at ASC
            """,
            (user_id, "active"),
        )

        return [self.mapper.from_row(row) for row in rows]