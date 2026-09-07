"""Interface for AI memory systems."""

from abc import ABC, abstractmethod
from typing import Any


class MemoryInterface(ABC):
    """Common contract for memory implementations."""

    @abstractmethod
    def store(self, key: str, value: Any) -> None:
        """Store a value under a key."""
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, key: str) -> Any:
        """Retrieve a value by key."""
        raise NotImplementedError

    @abstractmethod
    def update(self, key: str, value: Any) -> None:
        """Update an existing value."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a stored value."""
        raise NotImplementedError