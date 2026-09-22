"""Memory domain components."""

from core.memory.memory import (
    MemoryItem,
    MemoryStatus,
    MemoryType,
)

__all__ = [
    "MemoryItem",
    "MemoryStatus",
    "MemoryType",
    "MemoryService",
]


def __getattr__(name: str):
    """
    Lazily expose MemoryService.

    MemoryService depends on MemoryRepository, while
    MemoryRepository depends on the Memory domain models.
    Lazy loading prevents a circular import during package initialization.
    """

    if name == "MemoryService":
        from core.memory.memory_service import MemoryService

        return MemoryService

    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}"
    )