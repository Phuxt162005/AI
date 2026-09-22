"""Model evaluation persistence entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass
class EvaluationResult:
    evaluation_id: int | None
    model_version_id: int
    metric_name: str
    metric_value: float
    dataset_id: int | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.model_version_id <= 0:
            raise ValueError("model_version_id must be greater than zero")

        if not self.metric_name.strip():
            raise ValueError("metric_name must not be empty")

        if self.dataset_id is not None and self.dataset_id <= 0:
            raise ValueError("dataset_id must be greater than zero")