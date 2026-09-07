"""Interface for AI agents."""

from abc import ABC, abstractmethod
from typing import Any

from core.types import InputData, OutputData


class AgentInterface(ABC):
    """Common contract for AI Agent implementations."""

    @abstractmethod
    def process(self, input_data: InputData) -> OutputData:
        """Process an input and produce an output."""
        raise NotImplementedError

    @abstractmethod
    def decide(self, context: dict[str, Any]) -> dict[str, Any]:
        """Decide what action should be taken."""
        raise NotImplementedError

    @abstractmethod
    def respond(self, result: Any) -> OutputData:
        """Convert an internal result into an output."""
        raise NotImplementedError