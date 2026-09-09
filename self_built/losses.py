"""Self-built loss functions for ProjectAI."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod

from .tensor import Tensor


class Loss(ABC):
    """Base interface for loss functions."""

    def __init__(self) -> None:
        self._prediction: Tensor | None = None
        self._target: Tensor | None = None

    @abstractmethod
    def forward(self, prediction: Tensor, target: Tensor) -> float:
        raise NotImplementedError

    @abstractmethod
    def backward(self) -> Tensor:
        raise NotImplementedError


class MSELoss(Loss):
    """Mean Squared Error loss."""

    def forward(self, prediction: Tensor, target: Tensor) -> float:
        if prediction.shape != target.shape:
            raise ValueError(f"Prediction shape {prediction.shape} does not match target shape {target.shape}.")
        
        self._prediction = Tensor(prediction)
        self._target = Tensor(target)
        
        if prediction.size == 0:
            raise ValueError("MSELoss requires non-empty tensors.")
        return sum((float(p) - float(t)) ** 2 for p, t in zip(prediction._data, target._data)) / prediction.size

    def backward(self) -> Tensor:
        if self._prediction is None or self._target is None:
            raise RuntimeError("forward() must be called before backward().")
        
        scale = 2.0 / self._prediction.size
        return Tensor([scale * (float(p) - float(t)) for p, t in zip(self._prediction._data, self._target._data)], self._prediction.shape)


class BinaryCrossEntropyLoss(Loss):
    """Binary Cross-Entropy loss for probabilities in the range (0, 1)."""

    def forward(self, prediction: Tensor, target: Tensor) -> float:
        if prediction.shape != target.shape:
            raise ValueError(f"Prediction shape {prediction.shape} does not match target shape {target.shape}.")
        
        self._prediction = Tensor(prediction)
        self._target = Tensor(target)
        
        if prediction.size == 0:
            raise ValueError("BinaryCrossEntropyLoss requires non-empty tensors.")
        
        total = 0.0
        
        for probability, label in zip(prediction._data, target._data):
            probability = float(probability)
            label = float(label)
            if probability <= 0.0 or probability >= 1.0:
                raise ValueError("BinaryCrossEntropyLoss prediction values must be in the open interval (0, 1).")
            
            if label < 0.0 or label > 1.0:
                raise ValueError("BinaryCrossEntropyLoss target values must be in the range [0, 1].")
            total += -(label * math.log(probability) + (1.0 - label) * math.log(1.0 - probability))
        return total / prediction.size

    def backward(self) -> Tensor:
        if self._prediction is None or self._target is None:
            raise RuntimeError("forward() must be called before backward().")
        
        gradients = []
        
        for probability, label in zip(self._prediction._data, self._target._data):
            probability = float(probability)
            label = float(label)
            gradients.append((probability - label) / (probability * (1.0 - probability) * self._prediction.size))
        return Tensor(gradients, self._prediction.shape)