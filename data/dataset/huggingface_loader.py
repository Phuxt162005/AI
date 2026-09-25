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