from pathlib import Path

from training.checkpoint import (
    CheckpointManager,
)


def test_checkpoint_save_and_load(
    tmp_path: Path,
):
    manager = CheckpointManager(
        tmp_path
    )

    state = {
        "epoch": 2,
        "step": 10,
        "reason": "resource_limit_exceeded",
    }

    path = manager.save(
        state,
        filename="test.pkl",
    )

    assert path.exists()

    loaded = manager.load(path)

    assert loaded["epoch"] == 2
    assert loaded["step"] == 10
    assert (
        loaded["reason"]
        == "resource_limit_exceeded"
    )


def test_checkpoint_missing_file(
    tmp_path: Path,
):
    manager = CheckpointManager(
        tmp_path
    )

    missing = tmp_path / "missing.pkl"

    try:
        manager.load(missing)
        assert False
    except FileNotFoundError:
        assert True