import pytest

from training.monitoring import TrainingMonitor


def test_record_epoch_without_validation():
    monitor = TrainingMonitor()

    metrics = monitor.record_epoch(
        epoch=1,
        training_loss=0.4,
    )

    assert metrics.epoch == 1
    assert metrics.training_loss == 0.4
    assert metrics.validation_loss is None
    assert metrics.generalization_gap is None
    assert metrics.possible_overfitting is False


def test_record_epoch_calculates_generalization_gap():
    monitor = TrainingMonitor()

    metrics = monitor.record_epoch(
        epoch=1,
        training_loss=0.3,
        validation_loss=0.5,
    )

    assert metrics.generalization_gap == pytest.approx(0.2)
    assert metrics.possible_overfitting is True


def test_record_epoch_does_not_flag_positive_gap_as_false():
    monitor = TrainingMonitor()

    metrics = monitor.record_epoch(
        epoch=1,
        training_loss=0.5,
        validation_loss=0.3,
    )

    assert metrics.generalization_gap == pytest.approx(-0.2)
    assert metrics.possible_overfitting is False


@pytest.mark.parametrize(
    ("epoch", "training_loss", "validation_loss"),
    [
        (0, 0.5, 0.6),
        (1, -0.1, 0.6),
        (1, 0.5, -0.1),
    ],
)
def test_record_epoch_rejects_invalid_metrics(
    epoch,
    training_loss,
    validation_loss,
):
    monitor = TrainingMonitor()

    with pytest.raises(ValueError):
        monitor.record_epoch(
            epoch=epoch,
            training_loss=training_loss,
            validation_loss=validation_loss,
        )


def test_monitor_keeps_epoch_history():
    monitor = TrainingMonitor()

    monitor.record_epoch(1, 0.8, 0.9)
    monitor.record_epoch(2, 0.6, 0.7)

    assert len(monitor.history) == 2
    assert monitor.history[0].epoch == 1
    assert monitor.history[1].epoch == 2