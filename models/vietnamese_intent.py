"""Vietnamese intent classifier adapter for ProjectAI AI Core."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from core.interfaces import ModelInterface
from self_built.model import Model
from self_built.tensor import Tensor
from training.checkpoint import CheckpointManager
from training.registry import TrainingRegistry


class VietnameseIntentModel(ModelInterface):
    """Expose the trained Vietnamese intent classifier through ModelInterface."""

    def __init__(
        self,
        registry: TrainingRegistry,
        checkpoint_manager: CheckpointManager | None = None,
    ) -> None:
        if not isinstance(registry, TrainingRegistry):
            raise TypeError("registry must be a TrainingRegistry.")

        self.registry = registry
        self.checkpoint_manager = checkpoint_manager or CheckpointManager()
        self._model: Model | None = None
        self._vocabulary: dict[str, int] = {}
        self._labels: list[str] = []
        self._model_version: str | None = None
        self._checkpoint_path: Path | None = None

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"\w+", text.lower(), flags=re.UNICODE)

    def load(self, source: str | None = None) -> None:
        """Load a registered model version by its version identifier."""
        if not isinstance(source, str) or not source.strip():
            raise ValueError("source must be a registered model version.")

        registered_model = self.registry.get_model(source)
        checkpoint_path = Path(registered_model.checkpoint_path)
        checkpoint = self.checkpoint_manager.load(checkpoint_path)
        model = checkpoint.get("model")
        vocabulary = checkpoint.get("vocabulary")
        labels = checkpoint.get("labels")

        if not isinstance(model, Model):
            raise ValueError("Checkpoint does not contain a valid ProjectAI Model.")

        if not isinstance(vocabulary, dict) or not vocabulary:
            raise ValueError("Checkpoint does not contain a valid vocabulary.")

        if not isinstance(labels, list) or not labels:
            raise ValueError("Checkpoint does not contain valid labels.")

        if not all(
            isinstance(token, str) and isinstance(index, int)
            for token, index in vocabulary.items()
        ):
            raise ValueError("Checkpoint vocabulary has an invalid format.")

        if not all(isinstance(label, str) and label for label in labels):
            raise ValueError("Checkpoint labels have an invalid format.")

        model.eval()
        self._model = model
        self._vocabulary = vocabulary
        self._labels = labels
        self._model_version = source
        self._checkpoint_path = checkpoint_path

    def predict(self, inputs: Any) -> str:
        """Predict the intent label for one Vietnamese text input."""
        if self._model is None:
            raise RuntimeError("Model must be loaded before prediction.")

        if not isinstance(inputs, str):
            raise TypeError("Vietnamese intent input must be a string.")

        if not inputs.strip():
            raise ValueError("Vietnamese intent input must not be empty.")

        vector = [0.0] * len(self._vocabulary)

        for token in self._tokenize(inputs):
            index = self._vocabulary.get(token)
            if index is not None:
                vector[index] += 1.0

        logits = self._model.predict(Tensor([vector])).tolist()[0]

        if len(logits) != len(self._labels):
            raise ValueError("Model output size does not match the registered labels.")

        predicted_index = max(
            range(len(logits)),
            key=lambda index: float(logits[index]),
        )
        return self._labels[predicted_index]

    def save(self, destination: str) -> None:
        """Save the loaded model together with its inference metadata."""
        if self._model is None:
            raise RuntimeError("Model must be loaded before saving.")

        destination_path = Path(destination)
        manager = CheckpointManager(destination_path.parent)
        manager.save(
            {
                "model": self._model,
                "vocabulary": self._vocabulary,
                "labels": self._labels,
                "task": "vietnamese_intent_classification",
                "model_version": self._model_version,
            },
            filename=destination_path.name,
        )

    def metadata(self) -> dict[str, Any]:
        """Return metadata for the currently loaded intent model."""
        return {
            "task": "vietnamese_intent_classification",
            "model_version": self._model_version,
            "labels": list(self._labels),
            "vocabulary_size": len(self._vocabulary),
            "checkpoint_path": (
                str(self._checkpoint_path)
                if self._checkpoint_path is not None
                else None
            ),
        }