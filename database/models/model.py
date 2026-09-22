"""Model persistence entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class ModelStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class ModelVersionStatus(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"

class RegistryStatus(str, Enum):
    REGISTERED = "registered"
    ACTIVE = "active"
    RETIRED = "retired"

@dataclass
class Model:
    model_id: int | None
    name: str
    model_type: str
    framework: str = ""
    description: str = ""
    status: ModelStatus = ModelStatus.ACTIVE

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be empty")

        if not self.model_type.strip():
            raise ValueError("model_type must not be empty")

        if not isinstance(self.status, ModelStatus):
            self.status = ModelStatus(self.status)

@dataclass
class ModelVersion:
    model_version_id: int | None
    model_id: int
    version: str
    status: ModelVersionStatus = ModelVersionStatus.DEVELOPMENT
    training_run_id: int | None = None
    artifact_reference: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.model_id <= 0:
            raise ValueError("model_id must be greater than zero")

        if not self.version.strip():
            raise ValueError("version must not be empty")

        if (
            self.training_run_id is not None
            and self.training_run_id <= 0
        ):
            raise ValueError("training_run_id must be greater than zero")

        if not isinstance(
            self.status,
            ModelVersionStatus,
        ):
            self.status = ModelVersionStatus(self.status)

@dataclass
class ModelRegistry:
    registry_id: int | None
    model_version_id: int
    environment: str
    status: RegistryStatus = RegistryStatus.REGISTERED

    def __post_init__(self) -> None:
        if self.model_version_id <= 0:
            raise ValueError("model_version_id must be greater than zero")

        if not self.environment.strip():
            raise ValueError("environment must not be empty")

        if not isinstance(self.status, RegistryStatus):
            self.status = RegistryStatus(self.status)