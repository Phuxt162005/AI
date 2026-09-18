from data.sources.source import DataSource, SourceType


def test_create_data_source():
    source = DataSource(
        source_id="source_001",
        source_type=SourceType.FILE,
        name="training_data.json",
        location="data/raw/training_data.json",
    )

    assert source.source_id == "source_001"
    assert source.source_type == SourceType.FILE
    assert source.name == "training_data.json"


def test_source_to_dict():
    source = DataSource(
        source_id="source_002",
        source_type=SourceType.API,
        name="Example API",
        location="https://example.com/api",
    )

    result = source.to_dict()

    assert result["source_id"] == "source_002"
    assert result["source_type"] == "api"
    assert result["name"] == "Example API"


def test_source_type_accepts_string():
    source = DataSource(
        source_id="source_003",
        source_type="database",
        name="ProjectAI database",
    )

    assert source.source_type == SourceType.DATABASE