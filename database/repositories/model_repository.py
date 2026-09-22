"""Repositories for Model and Training data."""

from __future__ import annotations

import json
from typing import Any

from database.access.data_access import DataAccess
from database.access.repository import (
    BaseRepository,
    EntityMapper,
)
from database.models.evaluation import EvaluationResult
from database.models.model import (
    Model,
    ModelRegistry,
    ModelStatus,
    ModelVersion,
    ModelVersionStatus,
    RegistryStatus,
)
from database.models.training_run import (
    Dataset,
    DatasetStatus,
    TrainingConfiguration,
    TrainingRun,
    TrainingRunStatus,
)

def _json(value: Any) -> dict[str, Any]:
    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    if isinstance(value, str):
        return json.loads(value)

    return dict(value)

def _model_from_row(row: Any) -> Model:
    return Model(
        model_id=row.get("model_id"),
        name=row["name"],
        model_type=row["model_type"],
        framework=row.get("framework", ""),
        description=row.get("description", ""),
        status=ModelStatus(row.get("status", "active")),
    )
    
def _model_to_row(entity: Model) -> dict[str, Any]:
    row = {
        "name": entity.name,
        "model_type": entity.model_type,
        "framework": entity.framework,
        "description": entity.description,
        "status": entity.status.value,
    }

    if entity.model_id is not None:
        row["model_id"] = entity.model_id

    return row

class ModelRepository(BaseRepository[Model]):
    def __init__(self, data_access: DataAccess) -> None:
        super().__init__(
            data_access=data_access,
            table_name="models",
            mapper=EntityMapper(
                from_row=_model_from_row,
                to_row=_model_to_row,
            ),
            primary_key="model_id",
        )

    def list_active(self) -> list[Model]:
        rows = self.data_access.query(
            "SELECT * FROM `models` "
            "WHERE `status` = %s "
            "ORDER BY `model_id`",
            [ModelStatus.ACTIVE.value],
        )
        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

def _version_from_row(row: Any) -> ModelVersion:
    return ModelVersion(
        model_version_id=row.get("model_version_id"),
        model_id=row["model_id"],
        version=row["version"],
        status=ModelVersionStatus(row.get("status", "development")),
        training_run_id=row.get("training_run_id"),
        artifact_reference=row.get("artifact_reference"),
        parameters=_json(row.get("parameters")),
    )

def _version_to_row(entity: ModelVersion) -> dict[str, Any]:
    row = {
        "model_id": entity.model_id,
        "version": entity.version,
        "status": entity.status.value,
        "training_run_id": entity.training_run_id,
        "artifact_reference": entity.artifact_reference,
        "parameters": json.dumps(entity.parameters),
    }

    if entity.model_version_id is not None:
        row["model_version_id"] = entity.model_version_id

    return row

class ModelVersionRepository(BaseRepository[ModelVersion]):
    def __init__(self, data_access: DataAccess) -> None:
        super().__init__(
            data_access=data_access,
            table_name="model_versions",
            mapper=EntityMapper(
                from_row=_version_from_row,
                to_row=_version_to_row,
            ),
            primary_key="model_version_id",
        )

    def list_by_model(self, model_id: int) -> list[ModelVersion]:
        rows = self.data_access.query(
            "SELECT * FROM `model_versions` "
            "WHERE `model_id` = %s "
            "ORDER BY `model_version_id`",
            [model_id],
        )
        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

def _dataset_from_row(row: Any) -> Dataset:
    return Dataset(
        dataset_id=row.get("dataset_id"),
        name=row["name"],
        version=row["version"],
        storage_reference=row["storage_reference"],
        description=row.get("description", ""),
        status=DatasetStatus(
            row.get("status", "active")
        ),
        metadata=_json(row.get("metadata")),
    )

def _dataset_to_row(entity: Dataset) -> dict[str, Any]:
    row = {
        "name": entity.name,
        "version": entity.version,
        "storage_reference": entity.storage_reference,
        "description": entity.description,
        "status": entity.status.value,
        "metadata": json.dumps(entity.metadata),
    }

    if entity.dataset_id is not None:
        row["dataset_id"] = entity.dataset_id

    return row

class DatasetRepository(BaseRepository[Dataset]):
    def __init__(self, data_access: DataAccess) -> None:
        super().__init__(
            data_access=data_access,
            table_name="training_datasets",
            mapper=EntityMapper(
                from_row=_dataset_from_row,
                to_row=_dataset_to_row,
            ),
            primary_key="dataset_id",
        )

def _configuration_from_row(row: Any) -> TrainingConfiguration:
    return TrainingConfiguration(
        configuration_id=row.get("configuration_id"),
        version=row["version"],
        description=row.get("description", ""),
        parameters=_json(row.get("parameters")),
    )

def _configuration_to_row(entity: TrainingConfiguration) -> dict[str, Any]:
    row = {
        "version": entity.version,
        "description": entity.description,
        "parameters": json.dumps(entity.parameters),
    }

    if entity.configuration_id is not None:
        row["configuration_id"] = entity.configuration_id

    return row


class TrainingConfigurationRepository(BaseRepository[TrainingConfiguration]):
    def __init__(self, data_access: DataAccess) -> None:
        super().__init__(
            data_access=data_access,
            table_name="training_configurations",
            mapper=EntityMapper(
                from_row=_configuration_from_row,
                to_row=_configuration_to_row,
            ),
            primary_key="configuration_id",
        )

def _training_run_from_row(row: Any) -> TrainingRun:
    return TrainingRun(
        training_run_id=row.get("training_run_id"),
        dataset_id=row["dataset_id"],
        configuration_id=row["configuration_id"],
        status=TrainingRunStatus(
            row.get("status", "queued")
        ),
        started_at=row.get("started_at"),
        finished_at=row.get("finished_at"),
        metrics=_json(row.get("metrics")),
        error_message=row.get("error_message"),
    )

def _training_run_to_row(entity: TrainingRun) -> dict[str, Any]:
    row = {
        "dataset_id": entity.dataset_id,
        "configuration_id": entity.configuration_id,
        "status": entity.status.value,
        "started_at": entity.started_at,
        "finished_at": entity.finished_at,
        "metrics": json.dumps(entity.metrics),
        "error_message": entity.error_message,
    }

    if entity.training_run_id is not None:
        row["training_run_id"] = entity.training_run_id

    return row

class TrainingRunRepository(BaseRepository[TrainingRun]):
    def __init__(self, data_access: DataAccess) -> None:
        super().__init__(
            data_access=data_access,
            table_name="training_runs",
            mapper=EntityMapper(
                from_row=_training_run_from_row,
                to_row=_training_run_to_row,
            ),
            primary_key="training_run_id",
        )

def _evaluation_from_row(row: Any) -> EvaluationResult:
    return EvaluationResult(
        evaluation_id=row.get("evaluation_id"),
        model_version_id=row["model_version_id"],
        dataset_id=row.get("dataset_id"),
        metric_name=row["metric_name"],
        metric_value=float(row["metric_value"]),
        details=_json(row.get("details")),
    )

def _evaluation_to_row(entity: EvaluationResult) -> dict[str, Any]:
    row = {
        "model_version_id": entity.model_version_id,
        "dataset_id": entity.dataset_id,
        "metric_name": entity.metric_name,
        "metric_value": entity.metric_value,
        "details": json.dumps(entity.details),
    }

    if entity.evaluation_id is not None:
        row["evaluation_id"] = entity.evaluation_id

    return row

class EvaluationResultRepository(BaseRepository[EvaluationResult]):
    def __init__(self, data_access: DataAccess) -> None:
        super().__init__(
            data_access=data_access,
            table_name="evaluation_results",
            mapper=EntityMapper(
                from_row=_evaluation_from_row,
                to_row=_evaluation_to_row,
            ),
            primary_key="evaluation_id",
        )

    def list_by_model_version(self, model_version_id: int) -> list[EvaluationResult]:
        rows = self.data_access.query(
            "SELECT * FROM `evaluation_results` "
            "WHERE `model_version_id` = %s "
            "ORDER BY `evaluation_id`",
            [model_version_id],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]
        
def _registry_from_row(row: Any) -> ModelRegistry:
    return ModelRegistry(
        registry_id=row.get("registry_id"),
        model_version_id=row["model_version_id"],
        environment=row["environment"],
        status=RegistryStatus(
            row.get("status", "registered")
        ),
    )


def _registry_to_row(
    entity: ModelRegistry,
) -> dict[str, Any]:
    row = {
        "model_version_id": entity.model_version_id,
        "environment": entity.environment,
        "status": entity.status.value,
    }

    if entity.registry_id is not None:
        row["registry_id"] = entity.registry_id

    return row


class ModelRegistryRepository(
    BaseRepository[ModelRegistry]
):
    def __init__(self, data_access: DataAccess) -> None:
        super().__init__(
            data_access=data_access,
            table_name="model_registry",
            mapper=EntityMapper(
                from_row=_registry_from_row,
                to_row=_registry_to_row,
            ),
            primary_key="registry_id",
        )

    def get_by_environment(
        self,
        model_version_id: int,
        environment: str,
    ) -> ModelRegistry | None:
        row = self.data_access.query_one(
            "SELECT * FROM `model_registry` "
            "WHERE `model_version_id` = %s "
            "AND `environment` = %s",
            [
                model_version_id,
                environment,
            ],
        )

        if row is None:
            return None

        return self.mapper.map_from_row(row)