import pytest

from data.sources.internal import (
    InternalDatasetSource,
)


def create_source() -> InternalDatasetSource:
    return InternalDatasetSource(
        dataset_id="projectai_test",
        name="ProjectAI Test Dataset",
        dataset_type="instruction",
        local_path=(
            r"C:\DATA\AIDATA\raw\internal"
            r"\instruction"
        ),
    )


def test_internal_source_is_valid() -> None:
    source = create_source()

    assert source.dataset_id == "projectai_test"
    assert source.dataset_type == "instruction"
    assert source.language == "vi"
    assert source.version == "1.0.0"


def test_source_id_uses_internal_prefix() -> None:
    source = create_source()

    assert source.source_id == (
        "internal:projectai_test"
    )


def test_internal_source_supports_required_types() -> None:
    for dataset_type in (
        "instruction",
        "conversation",
        "personality",
        "emotion",
        "preference",
    ):
        source = InternalDatasetSource(
            dataset_id=f"projectai_{dataset_type}",
            name=f"ProjectAI {dataset_type}",
            dataset_type=dataset_type,
            local_path=(
                r"C:\DATA\AIDATA\raw\internal"
                rf"\{dataset_type}"
            ),
        )

        assert source.dataset_type == dataset_type


def test_invalid_dataset_type_is_rejected() -> None:
    with pytest.raises(ValueError):
        InternalDatasetSource(
            dataset_id="invalid",
            name="Invalid",
            dataset_type="unknown",
            local_path=r"C:\DATA\AIDATA\raw\internal",
        )