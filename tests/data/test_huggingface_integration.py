import os

import pytest

from data.dataset.huggingface_loader import (
    HuggingFaceDatasetLoader,
)
from data.sources.huggingface_catalog import (
    HF_DATASETS,
)


RUN_INTEGRATION = (
    os.getenv("PROJECTAI_RUN_HF_INTEGRATION")
    == "1"
)

pytestmark = pytest.mark.skipif(
    not RUN_INTEGRATION,
    reason=(
        "Hugging Face integration test is disabled. "
        "Set PROJECTAI_RUN_HF_INTEGRATION=1 to run."
    ),
)


def test_vietnamese_sft_10k_can_stream() -> None:
    source = HF_DATASETS["instruction_sft_10k"]

    loader = HuggingFaceDatasetLoader()

    samples = loader.preview(
        source,
        limit=3,
    )

    assert len(samples) == 3

    for sample in samples:
        assert isinstance(sample, dict)
        assert "prompt" in sample
        assert "response" in sample