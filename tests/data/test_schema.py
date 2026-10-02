import pytest
from data.schemas.data_schema import (
    DataRecord,
    DataSplit,
    DataType,
)


def test_create_data_record():
    record = DataRecord(
        record_id="record_001",
        data_type=DataType.TEXT,
        content="Hello ProjectAI",
    )

    assert record.record_id == "record_001"
    assert record.data_type == DataType.TEXT
    assert record.content == "Hello ProjectAI"


def test_data_record_supports_split():
    record = DataRecord(
        record_id="record_002",
        data_type=DataType.TEXT,
        content="training sample",
        split=DataSplit.TRAIN,
    )

    assert record.split == DataSplit.TRAIN


def test_data_record_to_dict():
    record = DataRecord(
        record_id="record_003",
        data_type=DataType.TEXT,
        content="hello",
    )

    result = record.to_dict()

    assert result["record_id"] == "record_003"
    assert result["data_type"] == "text"
    assert result["content"] == "hello"


def test_empty_record_id_is_rejected():
    try:
        DataRecord(
            record_id="",
            data_type=DataType.TEXT,
            content="hello",
        )
        assert False
    except ValueError:
        assert True

@pytest.mark.parametrize("record_id", ["", "   ", None, 123])
def test_invalid_record_id_is_rejected(record_id):
    with pytest.raises(ValueError):
        DataRecord(
            record_id=record_id,
            data_type=DataType.TEXT,
            content="hello",
        )


@pytest.mark.parametrize(
    "data_type",
    ["unknown", 123, None],
)
def test_invalid_data_type_is_rejected(data_type):
    with pytest.raises(ValueError):
        DataRecord(
            record_id="record_invalid_type",
            data_type=data_type,
            content="hello",
        )


def test_string_data_type_is_normalized_to_enum():
    record = DataRecord(
        record_id="record_string_type",
        data_type="text",
        content="hello",
    )

    assert record.data_type == DataType.TEXT


def test_invalid_tags_are_rejected():
    with pytest.raises(TypeError):
        DataRecord(
            record_id="record_invalid_tags",
            data_type=DataType.TEXT,
            content="hello",
            tags="not-a-list",
        )


def test_empty_tag_is_rejected():
    with pytest.raises(ValueError):
        DataRecord(
            record_id="record_empty_tag",
            data_type=DataType.TEXT,
            content="hello",
            tags=["valid", "   "],
        )


def test_record_to_dict_returns_independent_tags_list():
    record = DataRecord(
        record_id="record_tags",
        data_type=DataType.TEXT,
        content="hello",
        tags=["sample"],
    )

    result = record.to_dict()
    result["tags"].append("modified")

    assert record.tags == ["sample"]