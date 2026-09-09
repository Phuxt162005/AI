"""Evaluation utilities for ProjectAI."""

from __future__ import annotations

from self_built.model import Model
from self_built.tensor import Tensor


def evaluate_model(model: Model, inputs: Tensor, targets: Tensor) -> dict[str, float]:
    """Evaluate a model and return basic loss metrics."""
    model.eval()
    predictions = model.predict(inputs)
    loss = model.loss.forward(predictions, targets)
    return {"loss": float(loss)}