from data.validation.record_validator import (
    DatasetRecordValidator,
)


def test_instruction_records_are_valid() -> None:
    validator = DatasetRecordValidator()

    records = [
        {
            "instruction": "Giải thích AI là gì",
            "expected_output": "AI là trí tuệ nhân tạo.",
        },
        {
            "instruction": "Dịch câu này",
            "input": "Hello",
            "expected_output": "Xin chào",
        },
    ]

    result = validator.validate(
        records,
        "instruction",
    )

    assert result.valid_count == 2
    assert result.rejected_count == 0
    assert result.valid_ratio == 1.0


def test_instruction_missing_required_field() -> None:
    validator = DatasetRecordValidator()

    records = [
        {
            "instruction": "Giải thích AI",
        }
    ]

    result = validator.validate(
        records,
        "instruction",
    )

    assert result.valid_count == 0
    assert result.rejected_count == 1
    assert "expected_output" in result.errors[0]


def test_conversation_requires_messages() -> None:
    validator = DatasetRecordValidator()

    records = [
        {
            "messages": [],
        }
    ]

    result = validator.validate(
        records,
        "conversation",
    )

    assert result.rejected_count == 1
    assert any(
        "messages must not be empty" in error
        for error in result.errors
    )


def test_conversation_message_structure() -> None:
    validator = DatasetRecordValidator()

    records = [
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Xin chào",
                },
                {
                    "role": "assistant",
                    "content": "Xin chào bạn!",
                },
            ]
        }
    ]

    result = validator.validate(
        records,
        "conversation",
    )

    assert result.valid_count == 1
    assert result.rejected_count == 0


def test_personality_required_fields() -> None:
    validator = DatasetRecordValidator()

    records = [
        {
            "situation": "Người dùng hỏi",
            "context": "Cuộc trò chuyện bình thường",
            "desired_behavior": "Thân thiện",
            "expected_response": "Trả lời tự nhiên",
        }
    ]

    result = validator.validate(
        records,
        "personality",
    )

    assert result.valid_count == 1


def test_emotion_required_fields() -> None:
    validator = DatasetRecordValidator()

    records = [
        {
            "input": "Tôi rất vui hôm nay",
            "emotion": "joy",
            "expected_response": "Chúc mừng bạn!",
        }
    ]

    result = validator.validate(
        records,
        "emotion",
    )

    assert result.valid_count == 1


def test_preference_required_fields() -> None:
    validator = DatasetRecordValidator()

    records = [
        {
            "input": "Giải thích machine learning",
            "chosen": "Machine learning là...",
            "rejected": "Không biết.",
        }
    ]

    result = validator.validate(
        records,
        "preference",
    )

    assert result.valid_count == 1


def test_unsupported_dataset_type() -> None:
    validator = DatasetRecordValidator()

    try:
        validator.validate(
            [],
            "unknown",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError"
        )