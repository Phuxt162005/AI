from data.processing.chunker import TextChunker
from data.processing.cleaner import CleanRecord
from data.processing.preprocessor import (
    DataPreprocessor,
)


def make_record(
    record_id: str,
    content: str,
) -> CleanRecord:
    return CleanRecord(
        record_id=record_id,
        content=content,
        source_id="test",
        metadata_id="metadata_test",
    )


def test_preprocess_instruction() -> None:
    records = [
        make_record(
            "1",
            "Giải thích trí tuệ nhân tạo",
        ),
        make_record(
            "2",
            "Giải thích machine learning",
        ),
    ]

    preprocessor = DataPreprocessor()

    result = preprocessor.preprocess(
        records,
        "instruction",
        build_vocabulary=True,
    )

    assert result.input_count == 2
    assert result.output_count == 2

    assert result.records[0].tokens
    assert result.records[0].token_ids

    assert (
        result.records[0].metadata["preprocessed"]
        is True
    )


def test_preprocess_supported_dataset_types() -> None:
    preprocessor = DataPreprocessor()

    record = make_record(
        "1",
        "Dữ liệu ProjectAI",
    )

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
        result = preprocessor.preprocess(
            [record],
            dataset_type,
        )

        assert result.output_count == 1


def test_preprocess_rejects_unknown_dataset_type() -> None:
    preprocessor = DataPreprocessor()

    record = make_record(
        "1",
        "Dữ liệu",
    )

    try:
        preprocessor.preprocess(
            [record],
            "unknown",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_preprocess_normalizes_text() -> None:
    preprocessor = DataPreprocessor()

    record = make_record(
        "1",
        "Xin   chào\r\n\r\n\r\nProjectAI",
    )

    result = preprocessor.preprocess(
        [record],
        "instruction",
    )

    assert result.records[0].input == (
        "Xin chào\n\nProjectAI"
    )


def test_preprocess_builds_vocabulary() -> None:
    preprocessor = DataPreprocessor()

    records = [
        make_record(
            "1",
            "xin chao ProjectAI",
        ),
        make_record(
            "2",
            "ProjectAI AI assistant",
        ),
    ]

    result = preprocessor.preprocess(
        records,
        "pre_training",
        build_vocabulary=True,
    )

    assert result.output_count == 2

    vocabulary = (
        preprocessor.tokenizer.vocabulary
    )

    assert "xin" in vocabulary
    assert "ProjectAI" in vocabulary
    assert "assistant" in vocabulary


def test_preprocess_with_chunks() -> None:
    preprocessor = DataPreprocessor(
        chunker=TextChunker(
            chunk_size=3,
            overlap=1,
        )
    )

    record = make_record(
        "record1",
        "one two three four five six",
    )

    result = preprocessor.preprocess(
        [record],
        "pre_training",
        chunk=True,
    )

    assert result.input_count == 1
    assert result.chunk_count == 3
    assert result.output_count == 3

    assert (
        result.records[0].metadata[
            "source_record_id"
        ]
        == "record1"
    )


def test_chunking_requires_chunker() -> None:
    preprocessor = DataPreprocessor()

    record = make_record(
        "1",
        "one two three",
    )

    try:
        preprocessor.preprocess(
            [record],
            "pre_training",
            chunk=True,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_preprocessing_does_not_modify_input() -> None:
    record = make_record(
        "1",
        "  Xin   chào  ",
    )

    original = record.content

    preprocessor = DataPreprocessor()

    preprocessor.preprocess(
        [record],
        "instruction",
    )

    assert record.content == original