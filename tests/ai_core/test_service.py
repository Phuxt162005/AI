"""Tests for the AI Core service."""

from __future__ import annotations

from typing import Any

import pytest

from core.ai_core import AICoreService, ModelManager, ModelRuntime
from core.interfaces import ModelInterface
from core.types import InputData, InputType, OutputType


class DummyModel(ModelInterface):
    """Simple model used to test AICoreService."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.loaded = False

    def load(self, source: str | None = None) -> None:
        self.loaded = True

    def save(self, destination: str) -> None:
        if not self.loaded:
            raise RuntimeError("Model is not loaded.")

    def predict(self, inputs: Any) -> Any:
        if not self.loaded:
            raise RuntimeError("Model is not loaded.")

        return { "model": self.name, "input": inputs}

    def metadata(self) -> dict[str, Any]:
        return {"name": self.name, "type": "test"}

def create_service(model_name: str = "ConversationModel") -> AICoreService:
    """Create a service with one loaded dummy model."""
    model = DummyModel(model_name)
    runtime = ModelRuntime(model)
    manager = ModelManager()
    manager.register("conversation", runtime)
    manager.load("conversation")

    return AICoreService(manager)

def create_input(content: Any = "Hello AI") -> InputData:
    """Create a standard text input."""
    return InputData(type=InputType.TEXT, content=content)

def test_service_requires_model_manager() -> None:
    with pytest.raises(TypeError, match="ModelManager"):
        AICoreService(object())  # type: ignore[arg-type]

def test_service_accepts_output_type() -> None:
    manager = ModelManager()
    service = AICoreService(manager, output_type=OutputType.TEXT)

    assert service.output_type == OutputType.TEXT

def test_service_rejects_invalid_output_type() -> None:
    manager = ModelManager()

    with pytest.raises(TypeError, match="OutputType"):
        AICoreService(manager, output_type="text")

def test_service_exposes_model_manager() -> None:
    manager = ModelManager()
    service = AICoreService(manager)

    assert service.model_manager is manager

def test_run_returns_output_data() -> None:
    service = create_service()
    result = service.run("conversation", create_input())

    assert result.type == OutputType.TEXT
    assert result.content == {"model": "ConversationModel", "input": "Hello AI"}

def test_run_uses_selected_model() -> None:
    first_model = DummyModel("ConversationModel")
    second_model = DummyModel("ClassifierModel")
    first_runtime = ModelRuntime(first_model)
    second_runtime = ModelRuntime(second_model)
    manager = ModelManager()
    manager.register("conversation", first_runtime)
    manager.register("classifier", second_runtime)
    manager.load("conversation")
    manager.load("classifier")
    service = AICoreService(manager)
    conversation_result = service.run("conversation", create_input("Hello"))
    classifier_result = service.run("classifier", create_input("Classify this"))

    assert conversation_result.content["model"] == ("ConversationModel")
    assert classifier_result.content["model"] == ("ClassifierModel")

def test_run_preserves_input_metadata() -> None:
    manager = ModelManager()
    model = DummyModel("ConversationModel")
    runtime = ModelRuntime(model)
    manager.register("conversation", runtime)
    manager.load("conversation")
    service = AICoreService(manager)
    input_data = InputData(
        type=InputType.TEXT,
        content="Hello AI",
        metadata={
            "session_id": "session-1",
        },
    )
    result = service.run("conversation", input_data)

    assert result.metadata["session_id"] == "session-1"
    assert result.metadata["input_type"] == "text"

def test_run_rejects_invalid_input() -> None:
    service = create_service()

    with pytest.raises(TypeError, match="InputData"):
        service.run("conversation", "Hello AI",)

def test_run_rejects_empty_text_input() -> None:
    service = create_service()
    input_data = create_input("   ")

    with pytest.raises(ValueError, match="must not be empty"):
        service.run("conversation", input_data)

def test_run_missing_model_raises_error() -> None:
    manager = ModelManager()
    service = AICoreService(manager)

    with pytest.raises(KeyError, match="not registered"):
        service.run("conversation", create_input())

def test_run_unloaded_model_raises_error() -> None:
    manager = ModelManager()
    model = DummyModel("ConversationModel")
    runtime = ModelRuntime(model)
    manager.register("conversation", runtime)
    service = AICoreService(manager)

    with pytest.raises(RuntimeError,match="loaded"):
        service.run("conversation", create_input())

def test_run_propagates_model_error() -> None:
    class FailingModel(DummyModel):
        def predict(self, inputs: Any) -> Any:
            raise RuntimeError("Prediction failed.")

    model = FailingModel("FailingModel")
    runtime = ModelRuntime(model)
    manager = ModelManager()
    manager.register("failing", runtime)
    manager.load("failing")
    service = AICoreService(manager)
    
    with pytest.raises(RuntimeError, match="Prediction failed"):
        service.run("failing", create_input())

def test_service_uses_model_manager_and_pipeline_boundary() -> None:
    manager = ModelManager()
    model = DummyModel("ConversationModel")
    runtime = ModelRuntime(model)
    manager.register("conversation", runtime)
    manager.load("conversation")
    service = AICoreService(manager)
    result = service.run("conversation", create_input("Boundary test"))

    assert result.content["model"] == "ConversationModel"
    assert result.metadata["input_type"] == "text"