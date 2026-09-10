"""Tests for AI Core model management."""

from __future__ import annotations

from typing import Any

import pytest

from core.ai_core import ModelManager, ModelRuntime
from core.interfaces import ModelInterface


class DummyModel(ModelInterface):
    """Simple model used to test ModelManager."""

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

        return inputs

    def metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": "test",
        }


def create_runtime(name: str) -> ModelRuntime:
    """Create a runtime containing a dummy model."""
    return ModelRuntime(DummyModel(name))


def test_manager_starts_empty() -> None:
    manager = ModelManager()

    assert manager.list_models() == []


def test_register_model() -> None:
    manager = ModelManager()
    runtime = create_runtime("ConversationModel")

    manager.register("conversation", runtime)

    assert manager.has("conversation") is True
    assert manager.get("conversation") is runtime


def test_register_multiple_models() -> None:
    manager = ModelManager()

    conversation = create_runtime("ConversationModel")
    classifier = create_runtime("ClassifierModel")

    manager.register("conversation", conversation)
    manager.register("classifier", classifier)

    assert manager.list_models() == [
        "conversation",
        "classifier",
    ]


def test_register_rejects_duplicate_name() -> None:
    manager = ModelManager()

    manager.register(
        "conversation",
        create_runtime("ConversationModel"),
    )

    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        manager.register(
            "conversation",
            create_runtime("AnotherModel"),
        )


def test_register_rejects_invalid_runtime() -> None:
    manager = ModelManager()

    with pytest.raises(
        TypeError,
        match="ModelRuntime",
    ):
        manager.register("conversation", object())


def test_register_rejects_non_string_name() -> None:
    manager = ModelManager()
    runtime = create_runtime("ConversationModel")

    with pytest.raises(
        TypeError,
        match="model name must be a string",
    ):
        manager.register(123, runtime)  # type: ignore[arg-type]


def test_register_rejects_empty_name() -> None:
    manager = ModelManager()
    runtime = create_runtime("ConversationModel")

    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        manager.register("   ", runtime)


def test_get_missing_model_raises_error() -> None:
    manager = ModelManager()

    with pytest.raises(
        KeyError,
        match="not registered",
    ):
        manager.get("conversation")


def test_has_missing_model_returns_false() -> None:
    manager = ModelManager()

    assert manager.has("conversation") is False


def test_unregister_model() -> None:
    manager = ModelManager()

    manager.register(
        "conversation",
        create_runtime("ConversationModel"),
    )

    manager.unregister("conversation")

    assert manager.has("conversation") is False
    assert manager.list_models() == []


def test_unregister_missing_model_raises_error() -> None:
    manager = ModelManager()

    with pytest.raises(
        KeyError,
        match="not registered",
    ):
        manager.unregister("conversation")


def test_load_delegates_to_runtime() -> None:
    manager = ModelManager()
    runtime = create_runtime("ConversationModel")

    manager.register("conversation", runtime)

    assert runtime.is_ready is False

    manager.load("conversation")

    assert runtime.is_ready is True


def test_load_passes_source_to_runtime() -> None:
    class SourceModel(DummyModel):
        def __init__(self) -> None:
            super().__init__("SourceModel")
            self.source: str | None = None

        def load(self, source: str | None = None) -> None:
            self.source = source
            self.loaded = True

    model = SourceModel()
    runtime = ModelRuntime(model)

    manager = ModelManager()
    manager.register("source", runtime)

    manager.load("source", "model.bin")

    assert model.source == "model.bin"
    assert runtime.is_ready is True


def test_load_missing_model_raises_error() -> None:
    manager = ModelManager()

    with pytest.raises(
        KeyError,
        match="not registered",
    ):
        manager.load("conversation")


def test_list_models_returns_registered_names() -> None:
    manager = ModelManager()

    manager.register(
        "conversation",
        create_runtime("ConversationModel"),
    )
    manager.register(
        "classifier",
        create_runtime("ClassifierModel"),
    )

    assert manager.list_models() == [
        "conversation",
        "classifier",
    ]


def test_metadata_delegates_to_runtime() -> None:
    manager = ModelManager()
    manager.register("conversation", create_runtime("ConversationModel"))
    metadata = manager.metadata("conversation")
    assert metadata == {"name": "ConversationModel", "type": "test"}


def test_metadata_missing_model_raises_error() -> None:
    manager = ModelManager()

    with pytest.raises(KeyError, match="not registered"):
        manager.metadata("conversation")
        
def test_save_delegates_to_runtime() -> None:
    class SaveModel(DummyModel):
        def __init__(self) -> None:
            super().__init__("SaveModel")
            self.destination: str | None = None

        def save(self, destination: str) -> None:
            self.destination = destination

    model = SaveModel()
    runtime = ModelRuntime(model)
    manager = ModelManager()
    manager.register("save_model", runtime)
    manager.save("save_model", "model.bin")

    assert model.destination == "model.bin"


def test_manager_does_not_directly_depend_on_concrete_model() -> None:
    manager = ModelManager()
    runtime = create_runtime("ConversationModel")
    manager.register("conversation", runtime)

    assert manager.get("conversation") is runtime
    assert isinstance(manager.get("conversation"), ModelRuntime)
    
def test_save_unready_model_propagates_runtime_error() -> None:
    manager = ModelManager()
    manager.register("conversation", create_runtime("ConversationModel"))

    with pytest.raises(RuntimeError, match="loaded"):
        manager.save("conversation", "model.bin")