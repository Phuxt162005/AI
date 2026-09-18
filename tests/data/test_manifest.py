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