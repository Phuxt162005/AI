"""High-level service for AI Core."""

from __future__ import annotations

from core.types import InputData, OutputData, OutputType

from .inference import InferencePipeline
from .manager import ModelManager


class AICoreService:
    """Provide a stable high-level API for AI Core operations.

    AICoreService coordinates model selection through ModelManager
    and inference execution through InferencePipeline.
    It does not depend on concrete model implementations.
    """

    def __init__(
        self,
        model_manager: ModelManager,
        output_type: OutputType = OutputType.TEXT,
    ) -> None:
        if not isinstance(model_manager, ModelManager):
            raise TypeError(
                "model_manager must be an instance of ModelManager."
            )
        if not isinstance(output_type, OutputType):
            raise TypeError(
                "output_type must be an instance of OutputType."
            )

        self._model_manager = model_manager
        self._output_type = output_type

    @property
    def model_manager(self) -> ModelManager:
        """Return the model manager used by the service."""
        return self._model_manager

    @property
    def output_type(self) -> OutputType:
        """Return the output type produced by the service."""
        return self._output_type

    def run(
        self,
        model_name: str,
        input_data: InputData,
    ) -> OutputData:
        """Run inference using a registered model."""
        runtime = self._model_manager.get(model_name)
        pipeline = InferencePipeline(runtime=runtime, output_type=self._output_type)
        return pipeline.run(input_data)