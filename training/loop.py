"""Training loop."""

from __future__ import annotations

from dataclasses import dataclass

from self_built.model import Model
from self_built.tensor import Tensor


@dataclass
class TrainingHistory:
    """Training metrics collected during model training."""

    losses: list[float]


class TrainingLoop:
    """Controls the iterative training process of a model."""

    def __init__(self, model: Model) -> None:
        self.model = model

    def train_batch(self, inputs: Tensor, targets: Tensor) -> float:
        self.model.train()
        predictions = self.model.forward(inputs)
        loss_value = self.model.loss.forward(predictions, targets)
        gradient = self.model.loss.backward()
        self.model.network.backward(gradient)
        self.model.optimizer.step(self.model.network.gradients())
        return loss_value

    def fit(self, inputs: Tensor, targets: Tensor, epochs: int = 1) -> TrainingHistory:
        if epochs <= 0:
            raise ValueError("Number of epochs must be positive.")
        losses = []
        for _ in range(epochs):
            losses.append(self.train_batch(inputs, targets))
        return TrainingHistory(losses)