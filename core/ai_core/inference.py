"""Inference pipeline for AI Core."""

from __future__ import annotations

from typing import Any

from core.types import InputData, OutputData, OutputType

from .runtime import ModelRuntime


class InferencePipeline:
    """Process standardized input through an AI model runtime.

    The pipeline is responsible for validating input data, invoking
    ModelRuntime, and converting the model result into OutputData.
    It does not depend on any concrete model implementation.
    """

    def __init__(
        self,
        runtime: ModelRuntime,
        output_type: OutputType = OutputType.TEXT,
    ) -> None:
        if not isinstance(runtime, ModelRuntime):
            raise TypeError(
                "runtime must be an instance of ModelRuntime."
            )

        if not isinstance(output_type, OutputType):
            raise TypeError(
                "output_type must be an instance of OutputType."
            )

        self._runtime = runtime
        self._output_type = output_type

    @property
    def runtime(self) -> ModelRuntime:
        """Return the model runtime used by the pipeline."""
        return self._runtime

    @property
    def output_type(self) -> OutputType:
        """Return the output type produced by the pipeline."""
        return self._output_type

    def validate_input(self, input_data: InputData) -> None:
        """Validate standardized input data before inference."""
        if not isinstance(input_data, InputData):
            raise TypeError(
                "input_data must be an instance of InputData."
            )

        if input_data.content is None:
            raise ValueError(
                "input_data content must not be None."
            )

        if isinstance(input_data.content, str):
            if not input_data.content.strip():
                raise ValueError(
                    "input_data content must not be empty."
                )

    def run(self, input_data: InputData) -> OutputData:
        """Run inference and return standardized output data."""
        self.validate_input(input_data)

        if not self._runtime.is_ready:
            raise RuntimeError(
                "Model must be loaded before running inference."
            )

        result: Any = self._runtime.predict(input_data.content)

        metadata = dict(input_data.metadata)
        metadata["input_type"] = input_data.type.value

        return OutputData(
            type=self._output_type,
            content=result,
            metadata=metadata,
        )