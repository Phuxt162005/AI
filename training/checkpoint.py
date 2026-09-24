"""Training checkpoint management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch


class CheckpointManager:
    """Save and load training checkpoints."""

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
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        epoch: int,
        step: int,
        configuration: dict[str, Any],
        filename: str = "latest.pt",
    ) -> Path:
        path = self.directory / filename

        state = {
            "model_state_dict": (
                model.state_dict()
            ),
            "optimizer_state_dict": (
                optimizer.state_dict()
            ),
            "epoch": epoch,
            "step": step,
            "configuration": configuration,
        }

        torch.save(state, path)

        return path

    def load(
        self,
        path: str | Path,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
    ) -> dict[str, Any]:
        checkpoint = torch.load(
            path,
            map_location="cpu",
        )

        model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        optimizer.load_state_dict(
            checkpoint["optimizer_state_dict"]
        )

        return checkpoint