"""Self-built model and training utilities."""

from __future__ import annotations

from dataclasses import dataclass

from .layers import Layer
from .losses import Loss
from .optimizers import Optimizer
from .tensor import Tensor


@dataclass
class TrainingHistory:
    """Training metrics collected during model training."""

    losses: list[float]


class Model:
    """Trainable model built from a neural network and optimization components."""

    def __init__(self, network: Layer, loss: Loss, optimizer: Optimizer) -> None:
        self.network = network
        self.loss = loss
        self.optimizer = optimizer

    def forward(self, inputs: Tensor) -> Tensor:
        return self.network.forward(inputs)

    def predict(self, inputs: Tensor) -> Tensor:
        self.network.eval()
        return self.network.forward(inputs)

    def train(self) -> None:
        self.network.train()

    def eval(self) -> None:
        self.network.eval()

    def parameters(self) -> list[Tensor]:
        return self.network.parameters()

    def fit(self, inputs: Tensor, targets: Tensor, epochs: int = 1) -> TrainingHistory:
        if epochs <= 0:
            raise ValueError("Number of epochs must be positive.")
        self.train()
        losses = []
        for _ in range(epochs):
            predictions = self.forward(inputs)
            loss_value = self.loss.forward(predictions, targets)
            gradient = self.loss.backward()
            self.network.backward(gradient)
            self.optimizer.step(self.network.gradients())
            losses.append(loss_value)
        return TrainingHistory(losses)