from examples.training_end_to_end import run_training_demo


def test_end_to_end_training_learns_and_registers_model(tmp_path):
    result = run_training_demo(tmp_path)

    assert result["epochs_completed"] > 0
    assert result["best_epoch"] is not None

    assert (
        result["last_epoch_training_loss"]
        < result["first_epoch_training_loss"]
    )

    assert result["test_mse"] < 0.1
    assert result["test_mae"] >= 0.0

    assert result["checkpoint_path"]
    assert result["registry_path"]

    assert (tmp_path / "registry.json").exists()
    assert (tmp_path / "checkpoints").exists()