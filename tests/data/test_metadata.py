import pytest
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
    
@pytest.mark.parametrize(
    "size_bytes",
    [-1, 1.5, True, "100"],
)
def test_invalid_size_bytes_is_rejected(size_bytes):
    with pytest.raises((ValueError, TypeError)):
        MetadataSchema(
            metadata_id="meta_invalid_size",
            size_bytes=size_bytes,
        )


def test_invalid_attributes_type_is_rejected():
    with pytest.raises(TypeError):
        MetadataSchema(
            metadata_id="meta_invalid_attributes",
            attributes=["not", "a", "dict"],
        )


def test_metadata_manager_rejects_duplicate_id():
    manager = MetadataManager()
    manager.add(MetadataSchema(metadata_id="meta_duplicate"))

    with pytest.raises(ValueError):
        manager.add(MetadataSchema(metadata_id="meta_duplicate"))


def test_metadata_manager_rejects_invalid_update_without_mutating_data():
    manager = MetadataManager()
    metadata = MetadataSchema(
        metadata_id="meta_atomic_update",
        language="vi",
        size_bytes=100,
    )
    manager.add(metadata)

    with pytest.raises(ValueError):
        manager.update(
            "meta_atomic_update",
            language="en",
            size_bytes=-1,
        )

    stored = manager.get("meta_atomic_update")

    assert stored.language == "vi"
    assert stored.size_bytes == 100


def test_metadata_manager_rejects_unknown_update_field():
    manager = MetadataManager()
    manager.add(MetadataSchema(metadata_id="meta_unknown_field"))

    with pytest.raises(AttributeError):
        manager.update(
            "meta_unknown_field",
            unknown_field="value",
        )


def test_metadata_manager_rejects_missing_id():
    manager = MetadataManager()

    with pytest.raises(KeyError):
        manager.update("missing_metadata", language="vi")


def test_metadata_manager_remove():
    manager = MetadataManager()
    manager.add(MetadataSchema(metadata_id="meta_remove"))

    manager.remove("meta_remove")

    assert manager.get("meta_remove") is None
    assert manager.count() == 0