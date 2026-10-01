"""Load registered model versions for inference."""

from __future__ import annotations

from pathlib import Path

from self_built.model import Model
from training.checkpoint import CheckpointManager
from training.registry import TrainingRegistry

class ModelLoader:
    """Load a registered model version from its checkpoint."""

    def __init__(
        self,
        registry: TrainingRegistry,
        checkpoint_manager: CheckpointManager | None = None,
    ) -> None:
        if not isinstance(registry, TrainingRegistry):
            raise TypeError("registry must be a TrainingRegistry.")

        self.registry = registry
        self.checkpoint_manager = (checkpoint_manager or CheckpointManager())

    def load_model(self, model_version: str) -> Model:
        """Load a model by its registered version and prepare it for inference."""

        registered_model = self.registry.get_model(model_version)
        checkpoint_path = Path(registered_model.checkpoint_path)
        checkpoint = self.checkpoint_manager.load(checkpoint_path)
        model = checkpoint.get("model")

        if not isinstance(model, Model):
            raise ValueError("Checkpoint does not contain a valid ProjectAI Model.")

        model.eval()
        return model