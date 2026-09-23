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
    completed_stages: list[str] = field(default_factory=list)
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

    def __init__(
        self,
        stages: list[PipelineStage],
    ) -> None:
        self._stages = stages
        self._validate_stage_order()

    def run(self, initial_input: Any) -> PipelineResult:
        """Execute all configured pipeline stages."""

        value = initial_input
        completed: list[str] = []

        for stage in self._stages:
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

    def _validate_stage_order(self) -> None:
        names = [stage.name for stage in self._stages]

        if names != list(self.REQUIRED_STAGES):
            raise ValueError(
                "Pipeline stages must follow: "
                + " -> ".join(self.REQUIRED_STAGES)
            )