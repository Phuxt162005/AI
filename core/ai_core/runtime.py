"""Runtime for managing AI model lifecycle and inference."""

from __future__ import annotations

from enum import Enum
from typing import Any

from core.interfaces import ModelInterface


class ModelState(str, Enum):
    """Lifecycle states of an AI model."""

    CREATED = "created"
    LOADED = "loaded"
    READY = "ready"
    INFERENCE = "inference"


class ModelRuntime:
    """Manage the lifecycle and execution of an AI model.

    ModelRuntime provides a stable runtime boundary between the AI Core
    and a concrete model implementation.
    """

    def __init__(self, model: ModelInterface) -> None:
        if not isinstance(model, ModelInterface):
            raise TypeError(
                "model must implement ModelInterface."
            )

        self._model = model
        self._state = ModelState.CREATED

    @property
    def state(self) -> ModelState:
        """Return the current model lifecycle state."""
        return self._state

    @property
    def model(self) -> ModelInterface:
        """Return the model managed by this runtime."""
        return self._model

    @property
    def is_ready(self) -> bool:
        """Return whether the model is ready for inference."""
        return self._state == ModelState.READY

    def load(self, source: str | None = None) -> None:
        """Load the model and make it ready for inference."""
        try:
            self._model.load(source)
        except Exception as exc:
            self._state = ModelState.CREATED
            raise RuntimeError(
                "Failed to load AI model."
            ) from exc

        self._state = ModelState.LOADED
        self._state = ModelState.READY

    def predict(self, inputs: Any) -> Any:
        """Run inference using the loaded model."""
        if not self.is_ready:
            raise RuntimeError(
                "Model must be loaded before prediction."
            )

        self._state = ModelState.INFERENCE

        try:
            return self._model.predict(inputs)
        finally:
            self._state = ModelState.READY

    def save(self, destination: str) -> None:
        """Save the current model."""
        if not self.is_ready:
            raise RuntimeError(
                "Model must be loaded before saving."
            )

        self._model.save(destination)

    def metadata(self) -> dict[str, Any]:
        """Return metadata describing the managed model."""
        return self._model.metadata()