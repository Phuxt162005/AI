"""Load ProjectAI datasets directly from Hugging Face."""

from __future__ import annotations

from typing import Any

from data.sources.huggingface import HuggingFaceDatasetSource

class HuggingFaceDatasetLoader:
    """Load remote Hugging Face datasets."""

    def load(
        self,
        source: HuggingFaceDatasetSource,
        *,
        streaming: bool | None = None,
    ) -> Any:
        """Load a dataset from Hugging Face."""

        try:
            from datasets import load_dataset
        except ImportError as exc:
            raise RuntimeError(
                "Hugging Face Datasets is not installed. "
                "Install it with: pip install datasets"
            ) from exc

        use_streaming = (
            source.streaming
            if streaming is None
            else streaming
        )
        kwargs: dict[str, Any] = {
            "path": source.dataset_id,
            "split": source.split,
            "streaming": use_streaming,
        }

        if source.subset is not None:
            kwargs["name"] = source.subset
        return load_dataset(**kwargs)
    
    def preview(
        self,
        source: HuggingFaceDatasetSource,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        """Return a small preview without loading the full dataset."""

        if limit <= 0:
            raise ValueError("limit must be greater than zero")
        dataset = self.load(source, streaming=True)

        if not hasattr(dataset, "take"):
            raise TypeError("Streaming dataset does not support take()")

        return list(dataset.take(limit))