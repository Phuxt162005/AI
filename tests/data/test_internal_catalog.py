from data.sources.internal_catalog import (
    INTERNAL_DATASETS,
)


def test_internal_catalog_contains_required_datasets() -> None:
    required = {
        "instruction",
        "conversation",
        "personality",
        "emotion",
        "preference",
    }

    assert required.issubset(
        INTERNAL_DATASETS.keys()
    )


def test_internal_catalog_entries_are_valid() -> None:
    for source in INTERNAL_DATASETS.values():
        assert source.dataset_id
        assert source.name
        assert source.dataset_type
        assert source.local_path
        assert source.language == "vi"
        assert source.version


def test_internal_catalog_uses_aidata_paths() -> None:
    for source in INTERNAL_DATASETS.values():
        assert source.local_path.startswith(
            r"C:\DATA\AIDATA\raw\internal"
        )


def test_internal_catalog_uses_internal_source_ids() -> None:
    for source in INTERNAL_DATASETS.values():
        assert source.source_id.startswith(
            "internal:"
        )