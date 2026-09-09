"""Self-built neural network layers for ProjectAI."""

from __future__ import annotations

from abc import ABC, abstractmethod
from random import Random

from .tensor import Tensor


class Layer(ABC):
    """Base interface for neural network layers."""

    def __init__(self) -> None:
        self.training = True

    def train(self) -> None:
        self.training = True

    def eval(self) -> None:
        self.training = False

    @abstractmethod
    def forward(self, inputs: Tensor) -> Tensor:
        raise NotImplementedError

    @abstractmethod
    def backward(self, grad_output: Tensor) -> Tensor:
        raise NotImplementedError

    def parameters(self) -> list[Tensor]:
        return []

    def gradients(self) -> list[Tensor]:
        return []


class Linear(Layer):
    """Fully connected layer: y = xW + b."""

    def __init__(self, in_features: int, out_features: int, seed: int | None = 42) -> None:
        super().__init__()
        if in_features <= 0 or out_features <= 0:
            raise ValueError("Linear dimensions must be positive.")
        
        rng = Random(seed)
        limit = (2.0 / in_features) ** 0.5
        self.weight = Tensor([[rng.uniform(-limit, limit) for _ in range(out_features)] for _ in range(in_features)])
        self.bias = Tensor([0.0] * out_features)
        self.grad_weight = Tensor([[0.0] * out_features for _ in range(in_features)])
        self.grad_bias = Tensor([0.0] * out_features)
        self._inputs: Tensor | None = None

    def forward(self, inputs: Tensor) -> Tensor:
        if inputs.ndim == 1:
            if inputs.shape != (self.weight.shape[0],):
                raise ValueError(f"Expected input shape ({self.weight.shape[0]},), got {inputs.shape}.")
            inputs_2d = inputs.reshape(1, inputs.shape[0])
            output = _add_bias(inputs_2d @ self.weight, self.bias)
            self._inputs = inputs_2d
            return output.reshape(self.bias.shape[0])
        
        if inputs.ndim != 2 or inputs.shape[1] != self.weight.shape[0]:
            raise ValueError(f"Expected input shape (batch, {self.weight.shape[0]}), got {inputs.shape}.")
        
        self._inputs = inputs
        return _add_bias(inputs @ self.weight, self.bias)

    def backward(self, grad_output: Tensor) -> Tensor:
        if self._inputs is None:
            raise RuntimeError("forward() must be called before backward().")
        
        was_vector = grad_output.ndim == 1
        grad_2d = grad_output.reshape(1, grad_output.shape[0]) if was_vector else grad_output
        
        if grad_2d.ndim != 2 or grad_2d.shape[1] != self.bias.shape[0] or grad_2d.shape[0] != self._inputs.shape[0]:
            raise ValueError("Gradient shape does not match the layer output.")
        
        self.grad_weight = self._inputs.transpose() @ grad_2d
        self.grad_bias = Tensor([sum(grad_2d[row, col] for row in range(grad_2d.shape[0])) for col in range(grad_2d.shape[1])])
        grad_input = grad_2d @ self.weight.transpose()
        return grad_input.reshape(self._inputs.shape[1]) if was_vector else grad_input

    def parameters(self) -> list[Tensor]:
        return [self.weight, self.bias]

    def gradients(self) -> list[Tensor]:
        return [self.grad_weight, self.grad_bias]


class Activation(Layer, ABC):
    """Base class for element-wise activation layers."""

    def __init__(self) -> None:
        super().__init__()
        self._inputs: Tensor | None = None

    @abstractmethod
    def _activate(self, value: float) -> float:
        raise NotImplementedError

    @abstractmethod
    def _derivative(self, value: float) -> float:
        raise NotImplementedError

    def forward(self, inputs: Tensor) -> Tensor:
        self._inputs = Tensor(inputs)
        return Tensor([self._activate(float(value)) for value in inputs._data], inputs.shape)

    def backward(self, grad_output: Tensor) -> Tensor:
        if self._inputs is None:
            raise RuntimeError("forward() must be called before backward().")
        if grad_output.shape != self._inputs.shape:
            raise ValueError("Gradient shape must match activation input shape.")
        return Tensor([gradient * self._derivative(float(value)) for value, gradient in zip(self._inputs._data, grad_output._data)], self._inputs.shape)


class ReLU(Activation):
    """Rectified Linear Unit activation."""

    def _activate(self, value: float) -> float:
        return max(0.0, value)

    def _derivative(self, value: float) -> float:
        return 1.0 if value > 0.0 else 0.0


class Sigmoid(Activation):
    """Sigmoid activation."""

    def _activate(self, value: float) -> float:
        if value >= 0:
            z = 2.718281828459045 ** (-value)
            return 1.0 / (1.0 + z)
        z = 2.718281828459045 ** value
        return z / (1.0 + z)

    def _derivative(self, value: float) -> float:
        output = self._activate(value)
        return output * (1.0 - output)


class Tanh(Activation):
    """Hyperbolic tangent activation."""

    def _activate(self, value: float) -> float:
        positive = 2.718281828459045 ** (2.0 * value)
        return (positive - 1.0) / (positive + 1.0)

    def _derivative(self, value: float) -> float:
        output = self._activate(value)
        return 1.0 - output * output


def _add_bias(matrix: Tensor, bias: Tensor) -> Tensor:
    if matrix.ndim != 2 or bias.ndim != 1 or matrix.shape[1] != bias.shape[0]:
        raise ValueError("Bias shape does not match matrix output.")
    return Tensor([[matrix[row, col] + bias[col] for col in range(matrix.shape[1])] for row in range(matrix.shape[0])])