from pathlib import Path

from data.collection.raw_storage import (
    RawDataStorage,
)
from data.sources.huggingface_catalog import (
    HF_DATASETS,
)
from data.sources.internal_catalog import (
    INTERNAL_DATASETS,
)

def test_external_pretraining_path() -> None:
    storage = RawDataStorage(r"C:\DATA\AIDATA\raw")
    source = HF_DATASETS["pretraining_fsnaix"]
    path = storage.external_path(source)

    assert path == Path(
        r"C:\DATA\AIDATA\raw"
        r"\external\pretraining"
        r"\fsnaix_vietnamese_corpus_large"
    )


def test_external_instruction_path() -> None:
    storage = RawDataStorage(
        r"C:\DATA\AIDATA\raw"
    )

    source = HF_DATASETS["instruction_sft_10k"]

    path = storage.external_path(source)

    assert path == Path(
        r"C:\DATA\AIDATA\raw"
        r"\external\instruction"
        r"\vietnamese_sft_10k"
    )


def test_external_multimodal_path() -> None:
    storage = RawDataStorage(
        r"C:\DATA\AIDATA\raw"
    )

    source = HF_DATASETS["multimodal_vista"]

    path = storage.external_path(source)

    assert path == Path(
        r"C:\DATA\AIDATA\raw"
        r"\external\multimodal"
        r"\vista"
    )


def test_internal_instruction_path() -> None:
    storage = RawDataStorage(
        r"C:\DATA\AIDATA\raw"
    )

    source = INTERNAL_DATASETS["instruction"]

    path = storage.internal_path(source)

    assert path == Path(
        r"C:\DATA\AIDATA\raw"
        r"\internal\instruction"
    )


def test_internal_personality_path() -> None:
    storage = RawDataStorage(
        r"C:\DATA\AIDATA\raw"
    )

    source = INTERNAL_DATASETS["personality"]

    path = storage.internal_path(source)

    assert path == Path(
        r"C:\DATA\AIDATA\raw"
        r"\internal\personality"
    )


def test_create_external_directory(
    tmp_path: Path,
) -> None:
    storage = RawDataStorage(
        tmp_path / "raw"
    )

    source = HF_DATASETS["emotion_vsmec"]

    path = storage.create_external_directory(
        source
    )

    assert path.exists()
    assert path.is_dir()


def test_create_internal_directory(
    tmp_path: Path,
) -> None:
    storage = RawDataStorage(
        tmp_path / "raw"
    )

    source = INTERNAL_DATASETS["emotion"]

    path = storage.create_internal_directory(
        source
    )

    assert path.exists()
    assert path.is_dir()
