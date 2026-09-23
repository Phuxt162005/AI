"""Final AI data pipeline orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


StageFunction = Callable[[Any], Any]


@dataclass(frozen=True)
class PipelineStage:
    """One stage in the final data pipeline."""

    name: str
    function: StageFunction


@dataclass
class PipelineResult:
    """Result of a complete pipeline execution."""

    success: bool
    value: Any = None
    completed_stages: list[str] = field(
        default_factory=list
    )
    failed_stage: str | None = None
    error: str | None = None


class FinalDataPipeline:
    """Execute the final Data → Training → Evaluation flow."""

    REQUIRED_STAGES = (
        "source",
        "collection",
        "validation",
        "cleaning",
        "preprocessing",
        "storage",
        "dataset",
        "training",
        "evaluation",
    )

    RAG_STAGES = (
        "document",
        "chunking",
        "text_cleaning",
        "embedding_model",
        "embedding_vector",
        "vector_database",
    )

    def __init__(
        self,
        stages: list[PipelineStage],
    ) -> None:
        self._stages = stages
        self._validate_stage_order(
            names=[stage.name for stage in stages],
            required=self.REQUIRED_STAGES,
        )

    def run(
        self,
        initial_input: Any,
    ) -> PipelineResult:
        """Execute the complete training pipeline."""

        return self._run_stages(
            self._stages,
            initial_input,
        )

    @classmethod
    def create_rag_pipeline(
        cls,
        stages: list[PipelineStage],
    ) -> "FinalDataPipeline":
        """Create a pipeline for the RAG ingestion flow."""

        pipeline = object.__new__(cls)
        pipeline._stages = stages

        pipeline._validate_stage_order(
            names=[stage.name for stage in stages],
            required=cls.RAG_STAGES,
        )

        return pipeline

    def run_rag(
        self,
        initial_input: Any,
    ) -> PipelineResult:
        """Execute the RAG ingestion pipeline."""

        self._validate_stage_order(
            names=[
                stage.name
                for stage in self._stages
            ],
            required=self.RAG_STAGES,
        )

        return self._run_stages(
            self._stages,
            initial_input,
        )

    @staticmethod
    def _run_stages(
        stages: list[PipelineStage],
        initial_input: Any,
    ) -> PipelineResult:
        value = initial_input
        completed: list[str] = []

        for stage in stages:
            try:
                value = stage.function(value)
            except Exception as exc:
                return PipelineResult(
                    success=False,
                    value=value,
                    completed_stages=completed,
                    failed_stage=stage.name,
                    error=str(exc),
                )

            completed.append(stage.name)

        return PipelineResult(
            success=True,
            value=value,
            completed_stages=completed,
        )

    @staticmethod
    def _validate_stage_order(
        names: list[str],
        required: tuple[str, ...],
    ) -> None:
        if names != list(required):
            raise ValueError(
                "Pipeline stages must follow: "
                + " -> ".join(required)
            )