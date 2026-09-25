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
    access: str = "public"

    def __post_init__(self) -> None:
        if not self.dataset_id.strip():
            raise ValueError("dataset_id must not be empty")

        if not self.url.strip():
            raise ValueError("url must not be empty")

        if not self.url.startswith(
            "https://huggingface.co/datasets/"
        ):
            raise ValueError(
                "url must point to a Hugging Face dataset"
            )

        if not self.dataset_type.strip():
            raise ValueError(
                "dataset_type must not be empty"
            )

        if not self.split.strip():
            raise ValueError("split must not be empty")

        if not self.local_path.strip():
            raise ValueError(
                "local_path must not be empty"
            )

        if not self.language.strip():
            raise ValueError(
                "language must not be empty"
            )

        if self.access not in {
            "public",
            "gated",
            "restricted",
        }:
            raise ValueError(
                "access must be public, gated, "
                "or restricted"
            )

    @property
    def full_id(self) -> str:
        """Return dataset ID with its subset if present."""

        if self.subset:
            return f"{self.dataset_id}:{self.subset}"

        return self.dataset_id