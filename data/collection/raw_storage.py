"""Raw Data storage management for ProjectAI."""

from __future__ import annotations

from pathlib import Path

from data.sources.internal import (InternalDatasetSource)
from data.sources.huggingface import (HuggingFaceDatasetSource)

class RawDataStorage:
    """Manage Raw Data storage paths."""

    DATASET_TYPES = {
        "pre_training",
        "instruction",
        "conversation",
        "personality",
        "emotion",
        "multimodal",
        "preference",
    }

    INTERNAL_DATASET_TYPES = {
        "instruction",
        "conversation",
        "personality",
        "emotion",
        "preference",
    }

    def __init__(
        self,
        root: str | Path = r"C:\DATA\AIDATA\raw",
    ) -> None:
        self.root = Path(root)

    def external_path(self, source: HuggingFaceDatasetSource) -> Path:
        """Return the Raw Data path for an external dataset."""

        if source.dataset_type not in self.DATASET_TYPES:
            raise ValueError(
                f"Unsupported dataset type: "
                f"{source.dataset_type}"
            )

        return (
            self.root / "external" / self._normalize_type(
                source.dataset_type
            )
            / self._dataset_directory(source.local_path)
        )

    def internal_path(self, source: InternalDatasetSource) -> Path:
        """Return the Raw Data path for an internal dataset."""

        if (
            source.dataset_type
            not in self.INTERNAL_DATASET_TYPES
        ):
            raise ValueError(
                f"Unsupported internal dataset type: "
                f"{source.dataset_type}"
            )

        return (self.root / "internal" / source.dataset_type)

    def create_external_directory(self, source: HuggingFaceDatasetSource) -> Path:
        """Create and return an external Raw Data directory."""

        path = self.external_path(source)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def create_internal_directory(self, source: InternalDatasetSource) -> Path:
        """Create and return an internal Raw Data directory."""

        path = self.internal_path(source)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _normalize_type(dataset_type: str) -> str:
        """Normalize a dataset type for filesystem storage."""

        if dataset_type == "pre_training":
            return "pretraining"

        return dataset_type

    @staticmethod
    def _dataset_directory(local_path: str) -> str:
        """Extract the dataset directory name."""

        return Path(local_path).name