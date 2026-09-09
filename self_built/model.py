"""Self-built model for ProjectAI."""

from __future__ import annotations

from .layers import Layer
from .losses import Loss
from .optimizers import Optimizer
from .tensor import Tensor


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