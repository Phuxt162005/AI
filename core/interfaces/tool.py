"""Interface for external and internal tools."""

from abc import ABC, abstractmethod
from typing import Any


class ToolInterface(ABC):
    """Common contract for tools available to the AI Agent."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the tool name."""
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a human-readable tool description."""
        raise NotImplementedError

    @abstractmethod
    def execute(self, inputs: dict[str, Any]) -> Any:
        """Execute the tool with the provided inputs."""
        raise NotImplementedError