from data.dataset.training_builder import (
    TrainingDatasetBuilder,
)
from data.processing.preprocessor import (
    PreprocessedRecord,
)


def make_record(
    record_id: str,
    input_text: str,
    output: str | None = None,
) -> PreprocessedRecord:
    return PreprocessedRecord(
        record_id=record_id,
        input=input_text,
        output=output,
        tokens=input_text.split(),
        token_ids=list(
            range(len(input_text.split()))
        ),
        labels={"test": "label"},
        metadata={
            "source_id": "test_source",
        },
    )


def test_build_training_dataset() -> None:
    builder = TrainingDatasetBuilder(
        name="ProjectAI Instruction",
        version="1.0.0",
        dataset_type="instruction",
    )

    builder.add(
        make_record(
            "record_1",
            "Giải thích AI",
            "AI là trí tuệ nhân tạo.",
        )
    )

    dataset = builder.build()

    assert dataset.name == (
        "ProjectAI Instruction"
    )
    assert dataset.version == "1.0.0"
    assert dataset.dataset_type == "instruction"
    assert len(dataset) == 1


def test_build_multiple_records() -> None:
    builder = TrainingDatasetBuilder(
        name="ProjectAI Instruction",
        version="1.0.0",
        dataset_type="instruction",
    )

    records = [
        make_record(
            "1",
            "Câu hỏi 1",
            "Trả lời 1",
        ),
        make_record(
            "2",
            "Câu hỏi 2",
            "Trả lời 2",
        ),
        make_record(
            "3",
            "Câu hỏi 3",
            "Trả lời 3",
        ),
    ]

    builder.add_many(records)

    dataset = builder.build()

    assert len(dataset) == 3
    assert dataset.record_ids() == {
        "1",
        "2",
        "3",
    }


def test_preprocessed_information_is_preserved() -> None:
    builder = TrainingDatasetBuilder(
        name="ProjectAI",
        version="1.0.0",
        dataset_type="instruction",
    )

    record = make_record(
        "1",
        "Xin chào ProjectAI",
        "Xin chào!",
    )

    builder.add(record)

    dataset = builder.build()
    stored = dataset.records[0]

    assert stored.input == (
        "Xin chào ProjectAI"
    )
    assert stored.output == "Xin chào!"
    assert stored.labels["test"] == "label"

    assert stored.metadata["tokens"] == [
        "Xin",
        "chào",
        "ProjectAI",
    ]

    assert stored.metadata["token_ids"] == [
        0,
        1,
        2,
    ]

    assert stored.metadata["token_count"] == 3


def test_metadata_is_copied() -> None:
    record = make_record(
        "1",
        "Xin chào",
    )

    builder = TrainingDatasetBuilder(
        name="ProjectAI",
        version="1.0.0",
        dataset_type="instruction",
    )

    builder.add(record)

    stored = builder.build().records[0]

    assert stored.metadata["source_id"] == (
        "test_source"
    )
    assert stored.metadata["preprocessed"] is not True


def test_all_supported_dataset_types() -> None:
    dataset_types = [
        "pre_training",
        "instruction",
        "conversation",
        "personality",
        "emotion",
        "multimodal",
        "preference",
    ]

    for dataset_type in dataset_types:
        builder = TrainingDatasetBuilder(
            name="ProjectAI",
            version="1.0.0",
            dataset_type=dataset_type,
        )

        builder.add(
            make_record(
                "1",
                "Test data",
            )
        )

        dataset = builder.build()

        assert dataset.dataset_type == (
            dataset_type
        )
        assert len(dataset) == 1