"""Run the trained Vietnamese intent model through AI Core."""

from __future__ import annotations

from core.ai_core import AICoreService, ModelManager, ModelRuntime
from core.types import InputData, InputType, OutputType
from models.vietnamese_intent import VietnameseIntentModel
from training.registry import TrainingRegistry


def run_inference(
    model_version: str,
    text: str,
    registry_path: str = "artifacts/vietnamese_intent/registry.json",
) -> dict[str, object]:
    registry = TrainingRegistry(registry_path)

    intent_model = VietnameseIntentModel(registry)
    runtime = ModelRuntime(intent_model)
    manager = ModelManager()
    manager.register("vietnamese_intent", runtime)
    manager.load("vietnamese_intent", source=model_version)

    service = AICoreService(model_manager=manager, output_type=OutputType.TEXT)
    result = service.run(
        model_name="vietnamese_intent",
        input_data=InputData(type=InputType.TEXT, content=text),
    )

    return {
        "input": text,
        "predicted_intent": result.content,
        "model_metadata": manager.metadata("vietnamese_intent"),
    }


if __name__ == "__main__":
    registry = TrainingRegistry("artifacts/vietnamese_intent/registry.json")
    registered_models = registry.list_models()
    if not registered_models:
        raise RuntimeError("No registered Vietnamese intent model was found.")
    latest_model = registered_models[-1]

    import json

    print(
        json.dumps(
            run_inference(
                model_version=latest_model.model_version,
                text="Bạn có thể giúp tôi như thế nào?",
            ),
            ensure_ascii=False,
            indent=2,
        )
    )