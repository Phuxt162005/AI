"""Sequential neural network container."""

from __future__ import annotations

from .layers import Layer
from .tensor import Tensor

class Sequential(Layer):
    """Apply a sequence of layers from input to output."""

    def __init__(self, *layers: Layer) -> None:
        super().__init__()
        self.layers = list(layers)

    def add(self, layer: Layer) -> None:
        self.layers.append(layer)

    def forward(self, inputs: Tensor) -> Tensor:
        output = inputs
        for layer in self.layers:
            output = layer.forward(output)
        return output

    def backward(self, grad_output: Tensor) -> Tensor:
        gradient = grad_output
        for layer in reversed(self.layers):
            gradient = layer.backward(gradient)
        return gradient

    def train(self) -> None:
        super().train()
        for layer in self.layers:
            layer.train()

    def eval(self) -> None:
        super().eval()
        for layer in self.layers:
            layer.eval()

    def parameters(self) -> list[Tensor]:
        return [parameter for layer in self.layers for parameter in layer.parameters()]

    def gradients(self) -> list[Tensor]:
        return [gradient for layer in self.layers for gradient in layer.gradients()]