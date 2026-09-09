"""Self-built optimizers for ProjectAI."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .tensor import Tensor


class Optimizer(ABC):
    """Base interface for parameter optimization."""

    def __init__(self, parameters: list[Tensor], learning_rate: float = 0.01) -> None:
        if learning_rate <= 0.0:
            raise ValueError("Learning rate must be positive.")
        self.parameters = parameters
        self.learning_rate = learning_rate

    @abstractmethod
    def step(self, gradients: list[Tensor]) -> None:
        raise NotImplementedError

    def zero_grad(self) -> None:
        for parameter in self.parameters:
            for index in range(parameter.size):
                parameter._data[index] = 0.0


class SGD(Optimizer):
    """Stochastic Gradient Descent optimizer."""

    def step(self, gradients: list[Tensor]) -> None:
        if len(gradients) != len(self.parameters):
            raise ValueError("Number of gradients must match number of parameters.")
        for parameter, gradient in zip(self.parameters, gradients):
            if parameter.shape != gradient.shape:
                raise ValueError(f"Parameter shape {parameter.shape} does not match gradient shape {gradient.shape}.")
            for index in range(parameter.size):
                parameter._data[index] -= self.learning_rate * float(gradient._data[index])