"""Interface for AI models."""

from abc import ABC, abstractmethod
from typing import Any


class ModelInterface(ABC):
    """Common contract for every AI model in ProjectAI."""

    @abstractmethod
    def load(self, source: str | None = None) -> None:
        """Load model parameters or resources."""
        raise NotImplementedError

    @abstractmethod
    def save(self, destination: str) -> None:
        """Save model parameters or resources."""
        raise NotImplementedError

    @abstractmethod
    def predict(self, inputs: Any) -> Any:
        """Run inference on the given inputs."""
        raise NotImplementedError

    @abstractmethod
    def metadata(self) -> dict[str, Any]:
        """Return information describing the model."""
        raise NotImplementedError