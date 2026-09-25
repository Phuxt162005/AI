from unittest.mock import patch

from data.dataset.huggingface_loader import (
    HuggingFaceDatasetLoader,
)
from data.sources.huggingface import (
    HuggingFaceDatasetSource,
)


def test_loader_uses_streaming() -> None:
    source = HuggingFaceDatasetSource(
        dataset_id="test/dataset",
        url="https://huggingface.co/datasets/test/dataset",
        dataset_type="instruction",
        split="train",
        local_path=r"C:\DATA\AIDATA\raw\external\instruction\test",
    )

    loader = HuggingFaceDatasetLoader()

    with patch(
        "datasets.load_dataset",
        return_value="mock_dataset",
    ) as mocked_load:
        result = loader.load(source)

    assert result == "mock_dataset"

    mocked_load.assert_called_once_with(
        path="test/dataset",
        split="train",
        streaming=True,
    )