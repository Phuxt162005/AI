"""Model management for AI Core."""

from __future__ import annotations

from typing import Any

from .runtime import ModelRuntime


class ModelManager:
    """Manage registered AI model runtimes.

    ModelManager provides a central registry for model runtimes.
    It manages registration, lookup, loading, removal, and inspection
    of models without depending on concrete model implementations.
    """

    def __init__(self) -> None:
        self._models: dict[str, ModelRuntime] = {}

    def register(self, name: str, runtime: ModelRuntime) -> None:
        """Register a model runtime under a unique name."""
        self._validate_name(name)

        if not isinstance(runtime, ModelRuntime):
            raise TypeError(
                "runtime must be an instance of ModelRuntime."
            )

        if name in self._models:
            raise ValueError(
                f"Model '{name}' is already registered."
            )

        self._models[name] = runtime

    def unregister(self, name: str) -> None:
        """Remove a registered model."""
        self._validate_name(name)

        if name not in self._models:
            raise KeyError(
                f"Model '{name}' is not registered."
            )

        del self._models[name]

    def get(self, name: str) -> ModelRuntime:
        """Return the runtime registered under the given name."""
        self._validate_name(name)

        try:
            return self._models[name]
        except KeyError as exc:
            raise KeyError(
                f"Model '{name}' is not registered."
            ) from exc

    def has(self, name: str) -> bool:
        """Return whether a model is registered."""
        self._validate_name(name)
        return name in self._models

    def load(self, name: str, source: str | None = None) -> None:
        """Load a registered model through its runtime."""
        runtime = self.get(name)
        runtime.load(source)

    def save(self, name: str, destination: str) -> None:
        """Save a registered model through its runtime."""
        runtime = self.get(name)
        runtime.save(destination)

    def list_models(self) -> list[str]:
        """Return the names of all registered models."""
        return list(self._models.keys())

    def metadata(self, name: str) -> dict[str, Any]:
        """Return metadata for a registered model."""
        runtime = self.get(name)
        return runtime.metadata()

    @staticmethod
    def _validate_name(name: str) -> None:
        """Validate a model registry name."""
        if not isinstance(name, str):
            raise TypeError(
                "model name must be a string."
            )

        if not name.strip():
            raise ValueError(
                "model name must not be empty."
            )