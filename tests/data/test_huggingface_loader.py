from unittest.mock import patch

from data.dataset.huggingface_loader import (
    HuggingFaceDatasetLoader,
)
from data.sources.huggingface import (
    HuggingFaceDatasetSource,
)


def create_source() -> HuggingFaceDatasetSource:
    return HuggingFaceDatasetSource(
        dataset_id="test/dataset",
        url=(
            "https://huggingface.co/datasets/"
            "test/dataset"
        ),
        dataset_type="instruction",
        split="train",
        local_path=(
            r"C:\DATA\AIDATA\raw\external"
            r"\instruction\test"
        ),
    )


def test_loader_uses_streaming() -> None:
    source = create_source()
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


def test_loader_supports_subset() -> None:
    source = HuggingFaceDatasetSource(
        dataset_id="Vi-VLM/Vista",
        url=(
            "https://huggingface.co/datasets/"
            "Vi-VLM/Vista"
        ),
        dataset_type="multimodal",
        subset="vi_llava_conversation",
        split="train",
        local_path=(
            r"C:\DATA\AIDATA\raw\external"
            r"\multimodal\vista"
        ),
    )

    loader = HuggingFaceDatasetLoader()

    with patch(
        "datasets.load_dataset",
        return_value="mock_dataset",
    ) as mocked_load:
        loader.load(source)

    mocked_load.assert_called_once_with(
        path="Vi-VLM/Vista",
        name="vi_llava_conversation",
        split="train",
        streaming=True,
    )


def test_preview_uses_take() -> None:
    source = create_source()
    loader = HuggingFaceDatasetLoader()

    class MockIterableDataset:
        def take(self, limit: int):
            assert limit == 3

            return [
                {"text": "sample 1"},
                {"text": "sample 2"},
                {"text": "sample 3"},
            ]

    with patch(
        "datasets.load_dataset",
        return_value=MockIterableDataset(),
    ):
        result = loader.preview(
            source,
            limit=3,
        )

    assert len(result) == 3
    assert result[0]["text"] == "sample 1"


def test_preview_rejects_invalid_limit() -> None:
    source = create_source()
    loader = HuggingFaceDatasetLoader()

    try:
        loader.preview(source, limit=0)
    except ValueError as exc:
        assert "greater than zero" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )