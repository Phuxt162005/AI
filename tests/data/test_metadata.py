from data.metadata.metadata import MetadataManager
from data.schemas.metadata_schema import MetadataSchema


def test_create_metadata():
    metadata = MetadataSchema(
        metadata_id="meta_001",
        source_id="source_001",
        format="json",
        language="en",
    )

    assert metadata.metadata_id == "meta_001"
    assert metadata.source_id == "source_001"
    assert metadata.format == "json"


def test_metadata_manager_add_and_get():
    manager = MetadataManager()
    metadata = MetadataSchema(metadata_id="meta_001")
    manager.add(metadata)

    result = manager.get("meta_001")

    assert result is metadata
    assert manager.count() == 1


def test_metadata_manager_update():
    manager = MetadataManager()
    manager.add(MetadataSchema(metadata_id="meta_001", language="en"))
    manager.update("meta_001", language="vi")

    assert manager.get("meta_001").language == "vi"


def test_metadata_to_dict():
    metadata = MetadataSchema(metadata_id="meta_002", format="json")

    result = metadata.to_dict()

    assert result["metadata_id"] == "meta_002"
    assert result["format"] == "json"
    assert "created_at" in result