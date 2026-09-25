from data.processing.cleaner import CleanRecord
from data.quality.quality_control import (
    QualityController,
)
from data.validation.record_validator import (
    RecordValidationResult,
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


def test_quality_control_passes_good_dataset() -> None:
    records = [
        make_record("1", "Xin chào"),
        make_record("2", "Hôm nay bạn thế nào?"),
        make_record("3", "Tôi đang học AI."),
        make_record("4", "ProjectAI đang được xây dựng."),
    ]

    controller = QualityController(
        minimum_valid_ratio=0.95
    )

    result = controller.check(records)

    assert result.valid
    assert result.input_count == 4
    assert result.valid_count == 4
    assert result.rejected_count == 0


def test_quality_control_rejects_empty_content() -> None:
    records = [
        make_record("1", "Xin chào"),
        make_record("2", ""),
    ]

    controller = QualityController(
        minimum_valid_ratio=0.95
    )

    result = controller.check(records)

    assert not result.valid
    assert result.quality_result.empty_count == 1


def test_quality_control_detects_duplicate() -> None:
    records = [
        make_record("1", "Xin chào"),
        make_record("2", "Xin chào"),
    ]

    controller = QualityController(
        minimum_valid_ratio=0.95
    )

    result = controller.check(records)

    assert not result.valid
    assert result.quality_result.duplicate_count == 1


def test_quality_control_applies_validation_result() -> None:
    records = [
        make_record("1", "Xin chào"),
        make_record("2", "Dữ liệu hợp lệ"),
    ]

    validation_result = RecordValidationResult(
        valid_records=[
            {
                "instruction": "Xin chào",
                "expected_output": "Xin chào bạn",
            }
        ],
        rejected_records=[
            {
                "instruction": "Thiếu output",
            }
        ],
        errors=[
            "record 1: missing required field: "
            "expected_output"
        ],
    )

    controller = QualityController(
        minimum_valid_ratio=0.95
    )

    result = controller.check(
        records,
        validation_result=validation_result,
    )

    assert not result.valid
    assert result.input_count == 2
    assert result.rejected_count == 1
    assert result.valid_ratio == 0.5


def test_quality_control_rejects_low_valid_ratio() -> None:
    records = [
        make_record("1", "Dữ liệu"),
        make_record("2", "Dữ liệu 2"),
    ]

    validation_result = RecordValidationResult(
        valid_records=[
            {
                "instruction": "Dữ liệu",
                "expected_output": "Kết quả",
            }
        ],
        rejected_records=[
            {
                "instruction": "Lỗi",
            }
        ],
        errors=["invalid record"],
    )

    controller = QualityController(
        minimum_valid_ratio=1.0
    )

    result = controller.check(
        records,
        validation_result=validation_result,
    )

    assert not result.valid
    assert any(
        "valid ratio" in error
        for error in result.errors
    )