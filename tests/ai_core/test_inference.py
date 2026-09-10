"""Tests for the AI Core inference pipeline."""

from __future__ import annotations

from typing import Any

import pytest

from core.ai_core import InferencePipeline, ModelRuntime
from core.interfaces import ModelInterface
from core.types import InputData, InputType, OutputData, OutputType


class DummyModel(ModelInterface):
    """Simple model used to test InferencePipeline."""

    def __init__(self) -> None:
        self.loaded = False

    def load(self, source: str | None = None) -> None:
        self.loaded = True

    def save(self, destination: str) -> None:
        if not self.loaded:
            raise RuntimeError("Model is not loaded.")

    def predict(self, inputs: Any) -> Any:
        if not self.loaded:
            raise RuntimeError("Model is not loaded.")

        return {
            "response": inputs,
        }

    def metadata(self) -> dict[str, Any]:
        return {
            "name": "DummyModel",
            "type": "test",
        }


def create_pipeline() -> InferencePipeline:
    """Create a ready-to-use test pipeline."""
    model = DummyModel()
    runtime = ModelRuntime(model)
    runtime.load()

    return InferencePipeline(runtime)


def test_pipeline_accepts_model_runtime() -> None:
    model = DummyModel()
    runtime = ModelRuntime(model)

    pipeline = InferencePipeline(runtime)

    assert pipeline.runtime is runtime
    assert pipeline.output_type == OutputType.TEXT


def test_pipeline_rejects_invalid_runtime() -> None:
    with pytest.raises(TypeError, match="ModelRuntime"):
        InferencePipeline(object())


def test_pipeline_rejects_invalid_output_type() -> None:
    model = DummyModel()
    runtime = ModelRuntime(model)

    with pytest.raises(TypeError, match="OutputType"):
        InferencePipeline(runtime, output_type="text")


def test_pipeline_rejects_non_input_data() -> None:
    pipeline = create_pipeline()

    with pytest.raises(TypeError, match="InputData"):
        pipeline.run("hello")


def test_pipeline_rejects_none_content() -> None:
    pipeline = create_pipeline()

    input_data = InputData(
        type=InputType.TEXT,
        content=None,
    )

    with pytest.raises(ValueError, match="must not be None"):
        pipeline.run(input_data)


def test_pipeline_rejects_empty_text() -> None:
    pipeline = create_pipeline()

    input_data = InputData(
        type=InputType.TEXT,
        content="   ",
    )

    with pytest.raises(ValueError, match="must not be empty"):
        pipeline.run(input_data)


def test_pipeline_requires_ready_runtime() -> None:
    model = DummyModel()
    runtime = ModelRuntime(model)
    pipeline = InferencePipeline(runtime)

    input_data = InputData(
        type=InputType.TEXT,
        content="hello",
    )

    with pytest.raises(RuntimeError, match="Model must be loaded"):
        pipeline.run(input_data)


def test_pipeline_runs_model_inference() -> None:
    pipeline = create_pipeline()

    input_data = InputData(
        type=InputType.TEXT,
        content="hello",
    )

    output = pipeline.run(input_data)

    assert isinstance(output, OutputData)
    assert output.type == OutputType.TEXT
    assert output.content == {
        "response": "hello",
    }


def test_pipeline_preserves_input_metadata() -> None:
    pipeline = create_pipeline()

    input_data = InputData(
        type=InputType.TEXT,
        content="hello",
        metadata={
            "source": "test",
            "session_id": "123",
        },
    )

    output = pipeline.run(input_data)

    assert output.metadata["source"] == "test"
    assert output.metadata["session_id"] == "123"
    assert output.metadata["input_type"] == "text"


def test_pipeline_supports_custom_output_type() -> None:
    model = DummyModel()
    runtime = ModelRuntime(model)
    runtime.load()

    pipeline = InferencePipeline(
        runtime,
        output_type=OutputType.VOICE,
    )

    input_data = InputData(
        type=InputType.TEXT,
        content="hello",
    )

    output = pipeline.run(input_data)

    assert output.type == OutputType.VOICE
    assert output.content == {
        "response": "hello",
    }


def test_pipeline_does_not_modify_input_metadata() -> None:
    pipeline = create_pipeline()

    original_metadata = {
        "source": "test",
    }

    input_data = InputData(
        type=InputType.TEXT,
        content="hello",
        metadata=original_metadata,
    )

    pipeline.run(input_data)

    assert input_data.metadata == {
        "source": "test",
    }


def test_pipeline_propagates_model_error() -> None:
    class FailingModel(DummyModel):
        def predict(self, inputs: Any) -> Any:
            raise ValueError("Inference failed.")

    model = FailingModel()
    runtime = ModelRuntime(model)
    runtime.load()

    pipeline = InferencePipeline(runtime)

    input_data = InputData(
        type=InputType.TEXT,
        content="hello",
    )

    with pytest.raises(ValueError, match="Inference failed"):
        pipeline.run(input_data)