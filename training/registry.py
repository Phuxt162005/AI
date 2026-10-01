"""Metadata registry for training runs and model versions."""

from __future__ import annotations

import json
import os
import tempfile
import uuid

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def _utc_now() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()

def _new_id(prefix: str) -> str:
    """Create a unique identifier."""
    return f"{prefix}_{uuid.uuid4().hex}"

def _validate_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")

@dataclass
class TrainingRun:
    """Metadata describing one training execution."""

    run_id: str
    status: str
    started_at: str
    configuration: dict[str, Any]
    dataset: dict[str, Any]

    completed_at: str | None = None
    duration_seconds: float | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    checkpoint_path: str | None = None
    evaluation_path: str | None = None
    error: str | None = None

@dataclass
class ModelVersion:
    """Metadata describing a registered model version."""

    model_version: str
    run_id: str
    created_at: str
    checkpoint_path: str
    metrics: dict[str, Any] = field(default_factory=dict)
    description: str | None = None

class TrainingRegistry:
    """Persist training-run and model-version metadata in JSON."""

    def __init__(self, path: str | Path = "training/registry.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self._write({
                "schema_version": 1,
                "training_runs": {},
                "model_versions": {},
            })

    def _read(self) -> dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Invalid registry format.")

        data.setdefault("schema_version", 1)
        data.setdefault("training_runs", {})
        data.setdefault("model_versions", {})
        return data

    def _write(self, data: dict[str, Any]) -> None:
        """Atomically replace the registry JSON file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as file:
                temporary_path = Path(file.name)
                json.dump(data, file, indent=2, ensure_ascii=False)
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())

            temporary_path.replace(self.path)

        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()

    def create_run(
        self,
        configuration: dict[str, Any],
        dataset: dict[str, Any],
    ) -> TrainingRun:
        """Create and persist a run with status 'running'."""

        if not isinstance(configuration, dict):
            raise TypeError("configuration must be a dictionary.")

        if not isinstance(dataset, dict):
            raise TypeError("dataset must be a dictionary.")

        run = TrainingRun(
            run_id=_new_id("run"),
            status="running",
            started_at=_utc_now(),
            configuration=configuration,
            dataset=dataset,
        )
        data = self._read()
        data["training_runs"][run.run_id] = asdict(run)
        self._write(data)
        return run

    def complete_run(
        self,
        run_id: str,
        metrics: dict[str, Any],
        checkpoint_path: str | Path | None = None,
        evaluation_path: str | Path | None = None,
    ) -> TrainingRun:
        """Mark a run as completed and store its outputs."""

        if not isinstance(metrics, dict):
            raise TypeError("metrics must be a dictionary.")

        data = self._read()
        record = data["training_runs"].get(run_id)

        if record is None:
            raise KeyError(f"Unknown training run: {run_id}")

        if record["status"] != "running":
            raise ValueError("Only running training runs can be completed.")

        completed_at = datetime.now(timezone.utc)
        started_at = datetime.fromisoformat(record["started_at"])
        duration = max(0.0, (completed_at - started_at).total_seconds(),)
        record.update({
            "status": "completed",
            "completed_at": completed_at.isoformat(),
            "duration_seconds": duration,
            "metrics": metrics,
            "checkpoint_path": (str(checkpoint_path) if checkpoint_path is not None else None),
            "evaluation_path": (str(evaluation_path) if evaluation_path is not None else None),
        })
        self._write(data)
        return TrainingRun(**record)

    def fail_run(self, run_id: str, error: str) -> TrainingRun:
        """Mark a run as failed and store the error message."""

        _validate_text(error, "error")

        data = self._read()
        record = data["training_runs"].get(run_id)

        if record is None:
            raise KeyError(f"Unknown training run: {run_id}")

        if record["status"] != "running":
            raise ValueError("Only running training runs can fail.")

        completed_at = datetime.now(timezone.utc)
        started_at = datetime.fromisoformat(record["started_at"])

        record.update({
            "status": "failed",
            "completed_at": completed_at.isoformat(),
            "duration_seconds": max(0.0, (completed_at - started_at).total_seconds(),),
            "error": error,
        })
        self._write(data)
        return TrainingRun(**record)

    def register_model(
        self,
        model_version: str,
        run_id: str,
        checkpoint_path: str | Path,
        metrics: dict[str, Any] | None = None,
        description: str | None = None,
    ) -> ModelVersion:
        """Register a model version linked to a completed training run."""

        _validate_text(model_version, "model_version")

        if checkpoint_path is None:
            raise ValueError("checkpoint_path must be a non-empty string or Path.")

        checkpoint_path_text = str(checkpoint_path)
        _validate_text(checkpoint_path_text, "checkpoint_path")

        if metrics is not None and not isinstance(metrics, dict):
            raise TypeError("metrics must be a dictionary or None.")

        if description is not None and not isinstance(description, str):
            raise TypeError("description must be a string or None.")

        data = self._read()

        if model_version in data["model_versions"]:
            raise ValueError(f"Model version already exists: {model_version}")

        run = data["training_runs"].get(run_id)
        if run is None:
            raise KeyError(f"Unknown training run: {run_id}")

        if run["status"] != "completed":
            raise ValueError("A model can only be registered from a completed run.")

        model = ModelVersion(
            model_version=model_version,
            run_id=run_id,
            created_at=_utc_now(),
            checkpoint_path=checkpoint_path_text,
            metrics={} if metrics is None else metrics,
            description=description,
        )

        data["model_versions"][model_version] = asdict(model)
        self._write(data)
        return model

    def get_run(self, run_id: str) -> TrainingRun:
        """Retrieve one training run."""
        record = self._read()["training_runs"].get(run_id)

        if record is None:
            raise KeyError(f"Unknown training run: {run_id}")

        return TrainingRun(**record)

    def list_runs(self) -> list[TrainingRun]:
        """Return training runs ordered by start time."""
        records = self._read()["training_runs"].values()
        runs = [TrainingRun(**record) for record in records]
        return sorted(runs, key=lambda run: run.started_at)

    def get_model(self, model_version: str) -> ModelVersion:
        """Retrieve one registered model version."""
        record = self._read()["model_versions"].get(model_version)

        if record is None:
            raise KeyError(f"Unknown model version: {model_version}")

        return ModelVersion(**record)

    def list_models(self) -> list[ModelVersion]:
        """Return registered model versions ordered by creation time."""
        records = self._read()["model_versions"].values()
        models = [ModelVersion(**record) for record in records]
        return sorted(models, key=lambda model: model.created_at)