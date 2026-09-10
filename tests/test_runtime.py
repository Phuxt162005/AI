"""Tests for the AI Core model runtime."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from core.ai_core import ModelRuntime, ModelState
from core.interfaces import ModelInterface


class DummyModel(ModelInterface):
    """Simple model used to test ModelRuntime."""

    def __init__(self) -> None:
        self.loaded = False
        self.saved_to: str | None = None

    def load(self, source: str | None = None) -> None:
        self.loaded = True

    def save(self, destination: str) -> None:
        if not self.loaded:
            raise RuntimeError("Model is not loaded.")

        Path(destination).write_text(
            "dummy-model",
            encoding="utf-8",
        )
        self.saved_to = destination

    def predict(self, inputs: Any) -> Any:
        if not self.loaded:
            raise RuntimeError("Model is not loaded.")

        return {
            "result": inputs,
        }

    def metadata(self) -> dict[str, Any]:
        return {
            "name": "DummyModel",
            "type": "test",
        }


def test_runtime_starts_in_created_state() -> None:
    model = DummyModel()
    runtime = ModelRuntime(model)

    assert runtime.state == ModelState.CREATED
    assert runtime.is_ready is False


def test_load_makes_runtime_ready() -> None:
    model = DummyModel()
    runtime = ModelRuntime(model)

    runtime.load()

    assert model.loaded is True
    assert runtime.state == ModelState.READY
    assert runtime.is_ready is True


def test_predict_requires_loaded_model() -> None:
    model = DummyModel()
    runtime = ModelRuntime(model)

    with pytest.raises(RuntimeError, match="must be loaded"):
        runtime.predict("hello")


def test_predict_returns_model_result() -> None:
    model = DummyModel()
    runtime = ModelRuntime(model)

    runtime.load()

    result = runtime.predict("hello")

    assert result == {
        "result": "hello",
    }

    assert runtime.state == ModelState.READY


def test_predict_restores_ready_state_after_failure() -> None:
    class FailingModel(DummyModel):
        def predict(self, inputs: Any) -> Any:
            raise ValueError("Inference failed.")

    model = FailingModel()
    runtime = ModelRuntime(model)

    runtime.load()

    with pytest.raises(ValueError, match="Inference failed"):
        runtime.predict("hello")

    assert runtime.state == ModelState.READY


def test_save_requires_loaded_model(tmp_path: Path) -> None:
    model = DummyModel()
    runtime = ModelRuntime(model)

    destination = tmp_path / "model.bin"

    with pytest.raises(RuntimeError, match="must be loaded"):
        runtime.save(str(destination))


def test_save_delegates_to_model(tmp_path: Path) -> None:
    model = DummyModel()
    runtime = ModelRuntime(model)

    runtime.load()

    destination = tmp_path / "model.bin"

    runtime.save(str(destination))

    assert destination.exists()
    assert destination.read_text(encoding="utf-8") == "dummy-model"
    assert model.saved_to == str(destination)


def test_metadata_delegates_to_model() -> None:
    model = DummyModel()
    runtime = ModelRuntime(model)

    assert runtime.metadata() == {
        "name": "DummyModel",
        "type": "test",
    }


def test_runtime_rejects_invalid_model() -> None:
    with pytest.raises(TypeError, match="ModelInterface"):
        ModelRuntime(object())