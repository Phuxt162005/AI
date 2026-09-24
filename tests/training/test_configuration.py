import pytest

from training.configuration import (
    TrainingConfiguration,
)


def test_default_configuration():
    config = TrainingConfiguration()

    config.validate()

    assert config.batch_size == 1
    assert config.gradient_accumulation_steps == 8
    assert config.sequence_length == 128
    assert config.num_workers == 0
    assert config.mixed_precision is True
    assert config.resource_check_interval == 20


def test_invalid_batch_size():
    config = TrainingConfiguration(
        batch_size=0
    )

    with pytest.raises(ValueError):
        config.validate()


def test_invalid_sequence_length():
    config = TrainingConfiguration(
        sequence_length=0
    )

    with pytest.raises(ValueError):
        config.validate()


def test_invalid_worker_count():
    config = TrainingConfiguration(
        num_workers=-1
    )

    with pytest.raises(ValueError):
        config.validate()