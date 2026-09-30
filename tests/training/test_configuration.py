import pytest

from training.configuration import (
    TrainingConfiguration,
)


def test_default_configuration() -> None:
    config = TrainingConfiguration()

    config.validate()

    assert config.epochs == 1
    assert config.learning_rate == 0.001
    assert config.seed == 42

    assert config.batch_size == 1
    assert config.shuffle is True
    assert config.drop_last is False
    assert config.num_workers == 0

    assert config.sequence_length == 128
    assert config.gradient_accumulation_steps == 8
    assert config.mixed_precision is True

    assert config.resource_check_interval == 20


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"epochs": 0}, "epochs must be at least 1"),
        (
            {"learning_rate": 0},
            "learning_rate must be positive",
        ),
        (
            {"batch_size": 0},
            "batch_size must be at least 1",
        ),
        (
            {"gradient_accumulation_steps": 0},
            "gradient_accumulation_steps",
        ),
        (
            {"sequence_length": 0},
            "sequence_length must be at least 1",
        ),
        (
            {"num_workers": -1},
            "num_workers must not be negative",
        ),
        (
            {"resource_check_interval": 0},
            "resource_check_interval",
        ),
    ],
)
def test_invalid_configuration(
    kwargs: dict,
    message: str,
) -> None:
    config = TrainingConfiguration(**kwargs)

    with pytest.raises(ValueError, match=message):
        config.validate()


def test_invalid_dataset_type() -> None:
    config = TrainingConfiguration(
        dataset_type="unknown",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported dataset_type",
    ):
        config.validate()


def test_empty_dataset_name_is_rejected() -> None:
    config = TrainingConfiguration(
        dataset_name=" ",
    )

    with pytest.raises(
        ValueError,
        match="dataset_name must not be empty",
    ):
        config.validate()


def test_empty_dataset_version_is_rejected() -> None:
    config = TrainingConfiguration(
        dataset_version=" ",
    )

    with pytest.raises(
        ValueError,
        match="dataset_version must not be empty",
    ):
        config.validate()


def test_custom_configuration() -> None:
    config = TrainingConfiguration(
        epochs=5,
        learning_rate=0.0005,
        seed=123,
        batch_size=16,
        shuffle=True,
        drop_last=True,
        sequence_length=256,
        dataset_name="ProjectAI Instruction",
        dataset_version="1.0.0",
        dataset_type="instruction",
    )

    config.validate()

    assert config.epochs == 5
    assert config.learning_rate == 0.0005
    assert config.seed == 123
    assert config.batch_size == 16
    assert config.sequence_length == 256
    assert config.dataset_name == "ProjectAI Instruction"


def test_configuration_to_dict() -> None:
    config = TrainingConfiguration(
        epochs=3,
        learning_rate=0.0001,
        dataset_name="ProjectAI",
        dataset_version="1.0.0",
        dataset_type="instruction",
    )

    data = config.to_dict()

    assert data["epochs"] == 3
    assert data["learning_rate"] == 0.0001
    assert data["dataset_name"] == "ProjectAI"
    assert data["dataset_version"] == "1.0.0"
    assert data["dataset_type"] == "instruction"


def test_configuration_is_immutable() -> None:
    config = TrainingConfiguration()

    with pytest.raises(AttributeError):
        config.batch_size = 16