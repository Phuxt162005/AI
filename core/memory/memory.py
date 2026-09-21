"""Memory domain model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class MemoryType(str, Enum):
    """Supported memory categories."""

    WORKING = "working"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"

class MemoryStatus(str, Enum):
    """Memory lifecycle states."""

    ACTIVE = "active"
    EXPIRED = "expired"
    FORGOTTEN = "forgotten"

@dataclass
class MemoryItem:
    """
    A single memory item associated with a user.
    The fields follow the Memory Item definition from Part II.
    """

    memory_id: int | None
    user_id: int
    memory_type: MemoryType
    content: str
    importance: float = 0.5
    created_at: datetime | None = None
    updated_at: datetime | None = None
    expires_at: datetime | None = None
    status: MemoryStatus = MemoryStatus.ACTIVE

    def __post_init__(self) -> None:
        if self.user_id <= 0:
            raise ValueError("user_id must be greater than zero")

        if not self.content.strip():
            raise ValueError("content must not be empty")

        if not 0.0 <= self.importance <= 1.0:
            raise ValueError("importance must be between 0.0 and 1.0")

        if not isinstance(self.memory_type, MemoryType):
            self.memory_type = MemoryType(self.memory_type)

        if not isinstance(self.status, MemoryStatus):
            self.status = MemoryStatus(self.status)