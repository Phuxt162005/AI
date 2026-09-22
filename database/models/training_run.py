"""Training persistence entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

class DatasetStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"

class TrainingRunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Dataset:
    dataset_id: int | None
    name: str
    version: str
    storage_reference: str
    description: str = ""
    status: DatasetStatus = DatasetStatus.ACTIVE
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be empty")

        if not self.version.strip():
            raise ValueError("version must not be empty")

        if not self.storage_reference.strip():
            raise ValueError("storage_reference must not be empty")

        if not isinstance(self.status, DatasetStatus):
            self.status = DatasetStatus(self.status)

@dataclass
class TrainingConfiguration:
    configuration_id: int | None
    version: str
    parameters: dict[str, Any] = field(default_factory=dict)
    description: str = ""

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError("version must not be empty")

@dataclass
class TrainingRun:
    training_run_id: int | None
    dataset_id: int
    configuration_id: int
    status: TrainingRunStatus = TrainingRunStatus.QUEUED
    started_at: datetime | None = None
    finished_at: datetime | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None

    def __post_init__(self) -> None:
        if self.dataset_id <= 0:
            raise ValueError("dataset_id must be greater than zero")

        if self.configuration_id <= 0:
            raise ValueError("configuration_id must be greater than zero")

        if not isinstance(self.status, TrainingRunStatus):
            self.status = TrainingRunStatus(self.status)