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