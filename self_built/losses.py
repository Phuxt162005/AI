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
    
class SoftmaxCrossEntropyLoss(Loss):
    """Softmax cross-entropy for multiclass one-hot targets."""

    def __init__(self) -> None:
        super().__init__()
        self._probabilities: Tensor | None = None

    def forward(self, prediction: Tensor, target: Tensor) -> float:
        if prediction.ndim != 2 or target.ndim != 2:
            raise ValueError("Prediction and target must be 2-D tensors.")

        if prediction.shape != target.shape:
            raise ValueError(
                f"Prediction shape {prediction.shape} does not match "
                f"target shape {target.shape}."
            )

        batch_size, num_classes = prediction.shape
        if batch_size == 0 or num_classes < 2:
            raise ValueError("Cross-entropy requires a non-empty batch and 2+ classes.")

        probabilities = []
        total_loss = 0.0

        for row in range(batch_size):
            logits = [float(prediction[row, col]) for col in range(num_classes)]
            max_logit = max(logits)
            exponentials = [math.exp(value - max_logit) for value in logits]
            denominator = sum(exponentials)
            probs = [value / denominator for value in exponentials]
            probabilities.extend(probs)

            target_sum = 0.0
            for col in range(num_classes):
                label = float(target[row, col])
                if label < 0.0:
                    raise ValueError("Target values must be non-negative.")
                target_sum += label

                if label > 0.0:
                    total_loss -= label * math.log(max(probs[col], 1e-15))

            if abs(target_sum - 1.0) > 1e-6:
                raise ValueError("Each target row must sum to 1.")

        self._probabilities = Tensor(probabilities, prediction.shape)
        self._target = Tensor(target)
        return total_loss / batch_size

    def backward(self) -> Tensor:
        if self._probabilities is None or self._target is None:
            raise RuntimeError("forward() must be called before backward().")

        batch_size = self._probabilities.shape[0]
        return (self._probabilities - self._target) / batch_size