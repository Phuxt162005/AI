"""Internal dataset source definitions for ProjectAI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InternalDatasetSource:
    """Describe an internally created ProjectAI dataset."""

    dataset_id: str
    name: str
    dataset_type: str
    local_path: str
    language: str = "vi"
    version: str = "1.0.0"
    description: str = ""

    SUPPORTED_TYPES = {
        "instruction",
        "conversation",
        "personality",
        "emotion",
        "preference",
    }

    def __post_init__(self) -> None:
        if not self.dataset_id.strip():
            raise ValueError(
                "dataset_id must not be empty"
            )

        if not self.name.strip():
            raise ValueError(
                "name must not be empty"
            )

        if self.dataset_type not in self.SUPPORTED_TYPES:
            raise ValueError(
                f"Unsupported internal dataset type: "
                f"{self.dataset_type}"
            )

        if not self.local_path.strip():
            raise ValueError(
                "local_path must not be empty"
            )

        if not self.language.strip():
            raise ValueError(
                "language must not be empty"
            )

        if not self.version.strip():
            raise ValueError(
                "version must not be empty"
            )

    @property
    def source_id(self) -> str:
        """Return the source identifier."""

        return f"internal:{self.dataset_id}"

    def to_dict(self) -> dict[str, str]:
        """Convert the source to a serializable dictionary."""

        return {
            "dataset_id": self.dataset_id,
            "source_id": self.source_id,
            "name": self.name,
            "dataset_type": self.dataset_type,
            "local_path": self.local_path,
            "language": self.language,
            "version": self.version,
            "description": self.description,
        }