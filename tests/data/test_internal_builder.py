import pytest

from data.dataset.internal_builder import (
    InternalDatasetBuilder,
)
from data.sources.internal_catalog import (
    INTERNAL_DATASETS,
)


def test_instruction_dataset_builder() -> None:
    source = INTERNAL_DATASETS["instruction"]

    builder = InternalDatasetBuilder(source)

    builder.add(
        "instruction_001",
        {
            "instruction": "Giải thích thuật toán Dijkstra.",
            "input": "Trình bày ngắn gọn.",
            "expected_output": (
                "Dijkstra tìm đường đi ngắn nhất "
                "từ một đỉnh nguồn đến các đỉnh còn lại "
                "trong đồ thị có trọng số không âm."
            ),
        },
    )

    dataset = builder.build()

    assert len(dataset) == 1
    assert dataset.dataset_type == "instruction"
    assert dataset.records[0].record_id == (
        "instruction_001"
    )


def test_conversation_dataset_builder() -> None:
    source = INTERNAL_DATASETS["conversation"]

    builder = InternalDatasetBuilder(source)

    builder.add(
        "conversation_001",
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Bạn có thể giúp tôi không?",
                },
                {
                    "role": "assistant",
                    "content": "Được, tôi có thể giúp.",
                },
            ]
        },
    )

    dataset = builder.build()

    assert len(dataset) == 1
    assert isinstance(
        dataset.records[0].input,
        list,
    )


def test_personality_dataset_builder() -> None:
    source = INTERNAL_DATASETS["personality"]

    builder = InternalDatasetBuilder(source)

    builder.add(
        "personality_001",
        {
            "situation": "Người dùng gặp lỗi chương trình.",
            "context": "Người dùng đang cần hỗ trợ.",
            "desired_behavior": (
                "Kiên nhẫn, trực tiếp và giải thích rõ."
            ),
            "expected_response": (
                "Hãy gửi phần code đang gặp lỗi "
                "để tôi kiểm tra cùng bạn."
            ),
        },
    )

    dataset = builder.build()

    assert len(dataset) == 1
    assert dataset.records[0].output
    assert (
        dataset.records[0].labels["desired_behavior"]
        == "Kiên nhẫn, trực tiếp và giải thích rõ."
    )


def test_emotion_dataset_builder() -> None:
    source = INTERNAL_DATASETS["emotion"]

    builder = InternalDatasetBuilder(source)

    builder.add(
        "emotion_001",
        {
            "input": (
                "Tôi đã làm bài này cả ngày "
                "nhưng vẫn không chạy được."
            ),
            "emotion": "frustrated",
            "emotion_intensity": 0.8,
            "expected_response": (
                "Mình cùng kiểm tra từng bước "
                "để tìm nguyên nhân nhé."
            ),
        },
    )

    dataset = builder.build()

    assert len(dataset) == 1
    assert (
        dataset.records[0].labels["emotion"]
        == "frustrated"
    )
    assert (
        dataset.records[0].labels["emotion_intensity"]
        == 0.8
    )


def test_preference_dataset_builder() -> None:
    source = INTERNAL_DATASETS["preference"]

    builder = InternalDatasetBuilder(source)

    builder.add(
        "preference_001",
        {
            "input": "Giải thích thuật toán BFS.",
            "chosen": (
                "BFS duyệt đồ thị theo từng lớp "
                "bắt đầu từ đỉnh nguồn."
            ),
            "rejected": (
                "BFS là thuật toán sắp xếp dữ liệu."
            ),
        },
    )

    dataset = builder.build()

    assert len(dataset) == 1
    assert dataset.records[0].output == (
        "BFS duyệt đồ thị theo từng lớp "
        "bắt đầu từ đỉnh nguồn."
    )
    assert dataset.records[0].labels["rejected"] == (
        "BFS là thuật toán sắp xếp dữ liệu."
    )


def test_invalid_instruction_record_is_rejected() -> None:
    source = INTERNAL_DATASETS["instruction"]

    builder = InternalDatasetBuilder(source)

    with pytest.raises(ValueError):
        builder.add(
            "instruction_invalid",
            {
                "instruction": "Test",
            },
        )


def test_invalid_personality_record_is_rejected() -> None:
    source = INTERNAL_DATASETS["personality"]

    builder = InternalDatasetBuilder(source)

    with pytest.raises(ValueError):
        builder.add(
            "personality_invalid",
            {
                "situation": "Test",
            },
        )


def test_invalid_emotion_record_is_rejected() -> None:
    source = INTERNAL_DATASETS["emotion"]

    builder = InternalDatasetBuilder(source)

    with pytest.raises(ValueError):
        builder.add(
            "emotion_invalid",
            {
                "input": "Test",
                "emotion": "sad",
            },
        )


def test_invalid_preference_record_is_rejected() -> None:
    source = INTERNAL_DATASETS["preference"]

    builder = InternalDatasetBuilder(source)

    with pytest.raises(ValueError):
        builder.add(
            "preference_invalid",
            {
                "input": "Test",
                "chosen": "Good",
            },
        )


def test_add_many_builds_multiple_records() -> None:
    source = INTERNAL_DATASETS["instruction"]

    builder = InternalDatasetBuilder(source)

    builder.add_many(
        [
            {
                "record_id": "instruction_001",
                "instruction": "Câu hỏi 1",
                "expected_output": "Trả lời 1",
            },
            {
                "record_id": "instruction_002",
                "instruction": "Câu hỏi 2",
                "expected_output": "Trả lời 2",
            },
        ]
    )

    dataset = builder.build()

    assert len(dataset) == 2
    assert dataset.record_ids() == {
        "instruction_001",
        "instruction_002",
    }