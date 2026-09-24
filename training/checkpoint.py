"""Training checkpoint management."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any


class CheckpointManager:
    """Save and load generic training checkpoints."""

    def __init__(
        self,
        directory: str | Path = "checkpoints",
    ) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        state: dict[str, Any],
        filename: str = "latest.pkl",
    ) -> Path:
        if not isinstance(state, dict):
            raise TypeError(
                "Checkpoint state must be a dictionary."
            )

        path = self.directory / filename
        temporary_path = path.with_suffix(
            path.suffix + ".tmp"
        )

        with temporary_path.open("wb") as file:
            pickle.dump(
                state,
                file,
                protocol=pickle.HIGHEST_PROTOCOL,
            )

        temporary_path.replace(path)

        return path

    def load(
        self,
        path: str | Path,
    ) -> dict[str, Any]:
        checkpoint_path = Path(path)

        if not checkpoint_path.exists():
            raise FileNotFoundError(
                f"Checkpoint not found: {checkpoint_path}"
            )

        with checkpoint_path.open("rb") as file:
            state = pickle.load(file)

        if not isinstance(state, dict):
            raise ValueError(
                "Invalid checkpoint format."
            )

        return state