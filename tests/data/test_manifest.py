import pytest
from data.manifests.manifest import DatasetManifest
from data.schemas.data_schema import DataRecord, DataType


def create_record(record_id: str) -> DataRecord:
    return DataRecord(
        record_id=record_id,
        data_type=DataType.TEXT,
        content=f"content-{record_id}",
    )


def test_create_manifest():
    manifest = DatasetManifest(
        manifest_id="manifest_001",
        name="ProjectAI Dataset",
    )

    assert manifest.manifest_id == "manifest_001"
    assert manifest.name == "ProjectAI Dataset"
    assert manifest.record_count == 0


def test_add_record():
    manifest = DatasetManifest(
        manifest_id="manifest_001",
        name="ProjectAI Dataset",
    )

    record = create_record("record_001")

    manifest.add_record(record)

    assert manifest.record_count == 1
    assert manifest.get_record("record_001") is record


def test_remove_record():
    manifest = DatasetManifest(
        manifest_id="manifest_001",
        name="ProjectAI Dataset",
    )

    manifest.add_record(create_record("record_001"))
    manifest.remove_record("record_001")

    assert manifest.record_count == 0


def test_manifest_to_dict():
    manifest = DatasetManifest(
        manifest_id="manifest_001",
        name="ProjectAI Dataset",
    )

    manifest.add_record(create_record("record_001"))

    result = manifest.to_dict()

    assert result["manifest_id"] == "manifest_001"
    assert result["record_count"] == 1
    assert len(result["records"]) == 1
    
def test_manifest_rejects_duplicate_record():
    manifest = DatasetManifest(
        manifest_id="manifest_duplicate",
        name="Test Dataset",
    )

    manifest.add_record(create_record("record_001"))

    with pytest.raises(ValueError):
        manifest.add_record(create_record("record_001"))


def test_manifest_rejects_non_data_record():
    manifest = DatasetManifest(
        manifest_id="manifest_invalid_record",
        name="Test Dataset",
    )

    with pytest.raises(TypeError):
        manifest.add_record("not-a-data-record")


def test_manifest_rejects_empty_name():
    with pytest.raises(ValueError):
        DatasetManifest(
            manifest_id="manifest_empty_name",
            name="   ",
        )


def test_manifest_rejects_invalid_records_collection():
    with pytest.raises(TypeError):
        DatasetManifest(
            manifest_id="manifest_invalid_records",
            name="Test Dataset",
            records="not-a-list",
        )


def test_manifest_remove_missing_record():
    manifest = DatasetManifest(
        manifest_id="manifest_missing_record",
        name="Test Dataset",
    )

    with pytest.raises(KeyError):
        manifest.remove_record("missing_record")