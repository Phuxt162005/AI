"""Evaluation components for ProjectAI."""

from .evaluate import evaluate_model
from .dataset_evaluator import EvaluationResult, evaluate_dataset

__all__ = [
    "evaluate_model",
    "EvaluationResult",
    "evaluate_dataset",
]