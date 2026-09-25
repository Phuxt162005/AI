"""Hugging Face dataset source definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HuggingFaceDatasetSource:
    """Describe a dataset hosted on Hugging Face."""

    dataset_id: str
    url: str
    dataset_type: str
    split: str
    local_path: str
    subset: str | None = None
    license: str | None = None
    language: str = "vi"
    streaming: bool = True

    def __post_init__(self) -> None:
        if not self.dataset_id.strip():
            raise ValueError("dataset_id must not be empty")

        if not self.url.strip():
            raise ValueError("url must not be empty")

        if not self.dataset_type.strip():
            raise ValueError("dataset_type must not be empty")

        if not self.split.strip():
            raise ValueError("split must not be empty")

        if not self.local_path.strip():
            raise ValueError("local_path must not be empty")

    @property
    def full_id(self) -> str:
        """Return the Hugging Face dataset identifier."""

        if self.subset:
            return f"{self.dataset_id}:{self.subset}"

        return self.dataset_id