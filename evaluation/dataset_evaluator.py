"""Dataset-level evaluation utilities for ProjectAI."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from data.dataset.dataloader import DataBatch, DataLoader
from data.dataset.dataset import TrainingDataset
from self_built.model import Model
from self_built.tensor import Tensor

EvaluationBatchEncoder = Callable[[DataBatch], tuple[Tensor, Tensor]]

@dataclass(frozen=True)
class EvaluationResult:
    """Aggregated evaluation metrics for a dataset."""

    dataset_name: str
    dataset_version: str
    dataset_type: str
    evaluated_records: int
    batch_count: int
    loss: float
    mae: float
    mse: float

def evaluate_dataset(
    model: Model,
    dataset: TrainingDataset,
    batch_encoder: EvaluationBatchEncoder,
    batch_size: int = 32,
) -> EvaluationResult:
    """Evaluate a model on a dataset without updating model parameters."""

    if not callable(batch_encoder):
        raise TypeError("batch_encoder must be callable.")

    if batch_size <= 0:
        raise ValueError("batch_size must be positive.")

    if len(dataset) == 0:
        raise ValueError("Evaluation dataset must not be empty.")

    loader = DataLoader(
        dataset=dataset,
        batch_size=batch_size,
        shuffle=False,
        drop_last=False,
    )
    model.eval()

    total_loss = 0.0
    total_absolute_error = 0.0
    total_squared_error = 0.0
    total_elements = 0
    evaluated_records = 0
    batch_count = 0

    for batch in loader:
        inputs, targets = batch_encoder(batch)

        if not isinstance(inputs, Tensor):
            raise TypeError("batch_encoder must return Tensor inputs.")

        if not isinstance(targets, Tensor):
            raise TypeError("batch_encoder must return Tensor targets.")

        predictions = model.predict(inputs)
        if not isinstance(predictions, Tensor):
            raise TypeError("model.predict() must return a Tensor.")

        if predictions.shape != targets.shape:
            raise ValueError(
                "Prediction and target shapes must match: "
                f"{predictions.shape} != {targets.shape}."
            )

        if predictions.size == 0:
            raise ValueError("Evaluation predictions must not be empty.")

        batch_loss = float(model.loss.forward(predictions, targets))
        absolute_errors = [
            abs(float(prediction) - float(target))
            for prediction, target in zip(
                predictions._data,
                targets._data,
            )
        ]

        squared_errors = [error * error for error in absolute_errors]
        total_loss += batch_loss * len(batch)
        total_absolute_error += sum(absolute_errors)
        total_squared_error += sum(squared_errors)
        total_elements += len(absolute_errors)
        evaluated_records += len(batch)
        batch_count += 1

    if evaluated_records == 0 or total_elements == 0:
        raise ValueError("Evaluation produced no predictions.")

    return EvaluationResult(
        dataset_name=dataset.name,
        dataset_version=dataset.version,
        dataset_type=dataset.dataset_type,
        evaluated_records=evaluated_records,
        batch_count=batch_count,
        loss=total_loss / evaluated_records,
        mae=total_absolute_error / total_elements,
        mse=total_squared_error / total_elements,
    )