"""Application service for Memory management."""

from __future__ import annotations

from datetime import datetime

from core.memory.memory import (
    MemoryItem,
    MemoryStatus,
    MemoryType,
)
from database.repositories.memory_repository import MemoryRepository

class MemoryService:
    """
    Manage Memory lifecycle and user-isolated retrieval.
    The service keeps Memory business rules above the repository layer.
    """

    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository

    def save(self, memory: MemoryItem) -> MemoryItem:
        """Save a new Memory item."""

        existing = self.repository.find_by_content(
            memory.user_id,
            memory.content,
        )
        if existing is not None:
            return self.update(
                memory_id=existing.memory_id,
                user_id=memory.user_id,
                content=memory.content,
                memory_type=memory.memory_type,
                importance=memory.importance,
                expires_at=memory.expires_at,
            )
        return self.repository.create(memory)

    def get(
        self,
        memory_id: int,
        user_id: int,
    ) -> MemoryItem | None:
        """
        Retrieve one Memory belonging to the specified user.

        The repository performs the user isolation check.
        """

        return self.repository.get_for_user(
            memory_id=memory_id,
            user_id=user_id,
        )

    def retrieve(
        self,
        user_id: int,
        memory_type: MemoryType | None = None,
        limit: int = 20,
    ) -> list[MemoryItem]:
        """
        Retrieve active Memory for a user.
        This is structured retrieval. Semantic/vector retrieval
        is intentionally deferred to II-I.
        """

        if memory_type is None:
            return self.repository.list_by_user(
                user_id=user_id,
                limit=limit,
            )
        return self.repository.list_by_type(
            user_id=user_id,
            memory_type=memory_type,
            limit=limit,
        )

    def update(
        self,
        memory_id: int | None,
        user_id: int,
        content: str,
        memory_type: MemoryType,
        importance: float,
        expires_at: datetime | None = None,
    ) -> MemoryItem:
        """Update an existing Memory item."""

        if memory_id is None:
            raise ValueError("memory_id must not be None")

        if user_id <= 0:
            raise ValueError("user_id must be greater than zero")

        current = self.get(
            memory_id=memory_id,
            user_id=user_id,
        )

        if current is None:
            raise ValueError("Memory does not exist for this user")

        updated = MemoryItem(
            memory_id=current.memory_id,
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            importance=importance,
            created_at=current.created_at,
            updated_at=current.updated_at,
            expires_at=expires_at,
            status=MemoryStatus.ACTIVE,
        )

        return self.repository.update(
            entity_id=memory_id,
            entity=updated,
        )

    def forget(
        self,
        memory_id: int,
        user_id: int,
    ) -> None:
        """Forget a Memory item."""

        if self.get(
            memory_id=memory_id,
            user_id=user_id,
        ) is None:
            raise ValueError("Memory does not exist for this user")

        self.repository.mark_forgotten(
            memory_id=memory_id,
            user_id=user_id,
        )

    def delete(
        self,
        memory_id: int,
        user_id: int,
    ) -> None:
        """Permanently delete a Memory item belonging to a user."""

        if self.get(
            memory_id=memory_id,
            user_id=user_id,
        ) is None:
            raise ValueError("Memory does not exist for this user")

        sql = (
            "DELETE FROM `memories` "
            "WHERE `memory_id` = %s "
            "AND `user_id` = %s"
        )
        self.repository.data_access.execute(
            sql,
            [memory_id, user_id],
        )

    def expire(self) -> None:
        """Process Memory items whose expiration time has passed."""

        self.repository.expire_due()