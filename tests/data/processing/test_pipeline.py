from data.processing.balancer import DatasetBalancer
from data.processing.cleaner import CleanRecord
from data.processing.filter import DataFilter
from data.processing.pipeline import (
    DataProcessingPipeline,
)


def test_processing_pipeline():
    records = [
        CleanRecord(
            "1",
            "  ProjectAI   is an AI project.  ",
            source_id="source_001",
            metadata_id="metadata_001",
            attributes={"language": "en"},
        ),
        CleanRecord(
            "2",
            "ProjectAI   is an AI project.",
            source_id="source_001",
            metadata_id="metadata_002",
            attributes={"language": "en"},
        ),
        CleanRecord(
            "3",
            "A different useful record.",
            source_id="source_002",
            metadata_id="metadata_003",
            attributes={"language": "vi"},
        ),
        CleanRecord(
            "4",
            "X",
            source_id="source_003",
            metadata_id="metadata_004",
            attributes={"language": "vi"},
        ),
    ]

    pipeline = DataProcessingPipeline(
        data_filter=DataFilter(
            min_length=5
        ),
        balancer=DatasetBalancer(
            max_records_per_group=10
        ),
    )

    result = pipeline.process(
        records,
        use_near_deduplication=True,
        balance_group="language",
    )

    assert result.input_count == 4
    assert result.cleaned_count == 4
    assert result.deduplicated_count == 3
    assert result.filtered_count == 2
    assert result.normalized_count == 2
    assert result.balanced_count == 2
    assert result.output_count == 2


def test_pipeline_does_not_modify_input_list():
    records = [
        CleanRecord(
            "1",
            "  ProjectAI  ",
        )
    ]

    original_content = records[0].content
    pipeline = DataProcessingPipeline()
    pipeline.process(records)

    assert records[0].content == original_content