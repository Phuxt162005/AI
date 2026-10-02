"""Train a small Vietnamese intent classifier with ProjectAI's self-built engine."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from data.dataset.dataloader import DataBatch
from data.dataset.dataset import DatasetRecord, TrainingDataset
from self_built.layers import Linear, ReLU
from self_built.losses import SoftmaxCrossEntropyLoss
from self_built.model import Model
from self_built.network import Sequential
from self_built.optimizers import SGD
from self_built.tensor import Tensor
from training.checkpoint import CheckpointManager
from training.configuration import TrainingConfiguration
from training.execution import TrainingExecutor
from training.loop import TrainingLoop
from training.registry import TrainingRegistry


INTENT_EXAMPLES = {
    "greeting": [
        "Xin chào",
        "Chào bạn",
        "Chào buổi sáng",
        "Hello trợ lý",
        "Có ai ở đó không",
        "Xin chào bạn nhé",
        "Chào buổi tối",
        "Rất vui được gặp bạn",
        "Bạn khỏe không",
        "Ê trợ lý chào nhé",
        "Ê",
    ],
    "goodbye": [
        "Tạm biệt",
        "Hẹn gặp lại",
        "Chào nhé tôi đi đây",
        "Kết thúc cuộc trò chuyện",
        "Tôi phải đi rồi",
        "Gặp lại sau nhé",
        "Bye bye",
        "Bye",
        "Tạm biệt trợ lý",
        "Nói chuyện sau nhé",
        "Tôi đi đây",
    ],
    "thanks": [
        "Cảm ơn",
        "Cảm ơn bạn",
        "Xin cảm ơn",
        "Cảm ơn rất nhiều",
        "Bạn giúp ích quá",
        "Tôi biết ơn bạn",
        "Cảm ơn trợ lý nhé",
        "Hay quá cảm ơn",
        "Cảm ơn vì đã giúp",
        "Thật sự cảm ơn",
        "Cảm ơn nhiều nha",
    ],
    "weather": [
        "Thời tiết hôm nay thế nào",
        "Hôm nay có mưa không",
        "Dự báo thời tiết ngày mai",
        "Trời hôm nay có nắng không",
        "Nhiệt độ ngoài trời bao nhiêu",
        "Ngày mai thời tiết ra sao",
        "Có khả năng mưa vào chiều nay không",
        "Thời tiết Hà Nội hôm nay",
        "Hôm nay trời lạnh không",
        "Cho tôi xem dự báo thời tiết",
    ],
    "time": [
        "Bây giờ là mấy giờ",
        "Mấy giờ rồi",
        "Cho tôi biết thời gian hiện tại",
        "Hôm nay là ngày bao nhiêu",
        "Ngày hôm nay là thứ mấy",
        "Cho hỏi giờ hiện tại",
        "Bây giờ là ngày nào",
        "Thời gian hiện tại là bao nhiêu",
        "Hôm nay thứ mấy vậy",
        "Cho tôi biết hôm nay ngày mấy",
    ],
    "capability": [
        "Bạn có thể làm gì",
        "Bạn giúp được những việc nào",
        "Bạn có chức năng gì",
        "Bạn hỗ trợ tôi được không",
        "Bạn biết làm gì",
        "Khả năng của bạn là gì",
        "Tôi có thể nhờ bạn làm gì",
        "Bạn hỗ trợ những tác vụ nào",
        "Bạn có thể giúp tôi như thế nào",
        "Bạn làm được gì vậy",
    ],
}

LABELS = sorted(INTENT_EXAMPLES)
LABEL_TO_INDEX = {label: index for index, label in enumerate(LABELS)}


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower(), flags=re.UNICODE)


def build_datasets():
    train_records = []
    validation_records = []
    test_records = []

    for label, texts in INTENT_EXAMPLES.items():
        for index, text in enumerate(texts):
            record = DatasetRecord(
                record_id=f"{label}-{index:02d}",
                input=text,
                output=label,
                metadata={"source": "project_authored", "language": "vi"},
            )

            if index < 6:
                train_records.append(record)
            elif index < 8:
                validation_records.append(record)
            else:
                test_records.append(record)

    def make_dataset(name, records):
        return TrainingDataset(
            name=name,
            version="1.0.0",
            dataset_type="instruction",
            records=records,
            metadata={
                "language": "vi",
                "task": "intent_classification",
                "source": "project_authored_small_dataset",
            },
        )

    return (
        make_dataset("vi-intent-train", train_records),
        make_dataset("vi-intent-validation", validation_records),
        make_dataset("vi-intent-test", test_records),
    )


def build_vocabulary(dataset: TrainingDataset) -> dict[str, int]:
    tokens = sorted({
        token
        for record in dataset.records
        for token in tokenize(record.input)
    })
    return {token: index for index, token in enumerate(tokens)}


def encode_batch(batch: DataBatch, vocabulary: dict[str, int]) -> tuple[Tensor, Tensor]:
    inputs = []
    targets = []

    for text, label in zip(batch.inputs, batch.outputs):
        vector = [0.0] * len(vocabulary)
        for token in tokenize(text):
            index = vocabulary.get(token)
            if index is not None:
                vector[index] += 1.0

        inputs.append(vector)

        if label not in LABEL_TO_INDEX:
            raise ValueError(f"Unknown intent label: {label}")

        target = [0.0] * len(LABELS)
        target[LABEL_TO_INDEX[label]] = 1.0
        targets.append(target)

    return Tensor(inputs), Tensor(targets)


def predict_label(model: Model, text: str, vocabulary: dict[str, int]) -> str:
    vector = [0.0] * len(vocabulary)

    for token in tokenize(text):
        index = vocabulary.get(token)
        if index is not None:
            vector[index] += 1.0

    logits = model.predict(Tensor([vector]))
    row = [float(value) for value in logits.tolist()[0]]
    return LABELS[max(range(len(row)), key=row.__getitem__)]


def evaluate_accuracy(
    model: Model,
    dataset: TrainingDataset,
    vocabulary: dict[str, int],
) -> dict[str, Any]:
    correct = 0
    predictions = []
    confusion_matrix = {
        actual: {predicted: 0 for predicted in LABELS}
        for actual in LABELS
    }

    for record in dataset.records:
        predicted = predict_label(model, record.input, vocabulary)
        expected = record.output

        if expected not in confusion_matrix:
            raise ValueError(f"Unknown expected label: {expected}")

        if predicted not in confusion_matrix[expected]:
            raise ValueError(f"Unknown predicted label: {predicted}")

        is_correct = predicted == expected
        correct += int(is_correct)
        confusion_matrix[expected][predicted] += 1

        predictions.append({
            "text": record.input,
            "expected": expected,
            "predicted": predicted,
            "correct": is_correct,
        })

    total = len(dataset)
    per_class_metrics = {}

    for label in LABELS:
        true_positive = confusion_matrix[label][label]

        false_positive = sum(
            confusion_matrix[actual][label]
            for actual in LABELS
            if actual != label
        )
        false_negative = sum(
            confusion_matrix[label][predicted]
            for predicted in LABELS
            if predicted != label
        )

        support = sum(confusion_matrix[label].values())
        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive
            else 0.0
        )
        recall = (
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative
            else 0.0
        )
        f1_score = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )
        per_class_metrics[label] = {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "support": support,
        }

    macro_precision = sum(
        metrics["precision"]
        for metrics in per_class_metrics.values()
    ) / len(LABELS)
    macro_recall = sum(
        metrics["recall"]
        for metrics in per_class_metrics.values()
    ) / len(LABELS)
    macro_f1 = sum(
        metrics["f1_score"]
        for metrics in per_class_metrics.values()
    ) / len(LABELS)

    return {
        "accuracy": correct / total if total else 0.0,
        "correct": correct,
        "total": total,
        "confusion_matrix": confusion_matrix,
        "per_class_metrics": per_class_metrics,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "predictions": predictions,
    }


def run_training(output_dir: str | Path = "artifacts/vietnamese_intent"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train_dataset, validation_dataset, test_dataset = build_datasets()
    vocabulary = build_vocabulary(train_dataset)
    configuration = TrainingConfiguration(
        epochs=120,
        learning_rate=0.05,
        seed=42,
        batch_size=8,
        shuffle=True,
        dataset_name=train_dataset.name,
        dataset_version=train_dataset.version,
        dataset_type=train_dataset.dataset_type,
    )
    configuration.validate()
    network = Sequential(
        Linear(len(vocabulary), 32, seed=42),
        ReLU(),
        Linear(32, len(LABELS), seed=43),
    )
    model = Model(
        network=network,
        loss=SoftmaxCrossEntropyLoss(),
        optimizer=SGD(
            parameters=network.parameters(),
            learning_rate=configuration.learning_rate,
        ),
    )
    checkpoint_manager = CheckpointManager(output_dir / "checkpoints")
    loop = TrainingLoop(
        model=model,
        checkpoint_manager=checkpoint_manager,
        configuration=configuration,
    )
    train_encoder = lambda batch: encode_batch(batch, vocabulary)
    validation_encoder = lambda batch: encode_batch(batch, vocabulary)
    executor = TrainingExecutor(
        training_loop=loop,
        dataset=train_dataset,
        batch_encoder=train_encoder,
        validation_dataset=validation_dataset,
        validation_encoder=validation_encoder,
        early_stopping_patience=20,
        min_delta=1e-5,
    )
    registry = TrainingRegistry(output_dir / "registry.json")
    run = registry.create_run(
        configuration=configuration.to_dict(),
        dataset={
            "name": train_dataset.name,
            "version": train_dataset.version,
            "dataset_type": train_dataset.dataset_type,
            "train_records": len(train_dataset),
            "validation_records": len(validation_dataset),
            "test_records": len(test_dataset),
            "source": "project_authored_small_dataset",
        },
    )

    try:
        history = executor.run()
        if history.stopped_safely:
            raise RuntimeError(history.stop_reason or "Training stopped safely.")

        if history.checkpoint_path is None:
            raise RuntimeError("Training did not produce a best checkpoint.")

        test_metrics = evaluate_accuracy(model, test_dataset, vocabulary)
        if history.epoch_metrics:
            first_loss = history.epoch_metrics[0]["training_loss"]
            final_loss = history.epoch_metrics[-1]["training_loss"]
        else:
            raise RuntimeError("Training produced no epoch metrics.")

        result = {
            "run_id": run.run_id,
            "task": "Vietnamese intent classification",
            "labels": LABELS,
            "vocabulary_size": len(vocabulary),
            "train_records": len(train_dataset),
            "validation_records": len(validation_dataset),
            "test_records": len(test_dataset),
            "epochs_completed": len(history.epoch_metrics),
            "first_training_loss": first_loss,
            "final_training_loss": final_loss,
            "best_validation_loss": history.best_validation_loss,
            "test_accuracy": test_metrics["accuracy"],
            "test_correct": test_metrics["correct"],
            "test_total": test_metrics["total"],
            "confusion_matrix": test_metrics["confusion_matrix"],
            "per_class_metrics": test_metrics["per_class_metrics"],
            "macro_precision": test_metrics["macro_precision"],
            "macro_recall": test_metrics["macro_recall"],
            "macro_f1": test_metrics["macro_f1"],
            "checkpoint_path": history.checkpoint_path,
            "predictions": test_metrics["predictions"],
        }

        with (output_dir / "metrics.json").open("w", encoding="utf-8") as file:
            json.dump(result, file, ensure_ascii=False, indent=2)

        registry.complete_run(
            run_id=run.run_id,
            metrics={
                "final_training_loss": final_loss,
                "best_validation_loss": history.best_validation_loss,
                "test_accuracy": test_metrics["accuracy"],
            },
            checkpoint_path=history.checkpoint_path,
        )

        model_version = f"vi-intent-{run.run_id}"
        registry.register_model(
            model_version=model_version,
            run_id=run.run_id,
            checkpoint_path=history.checkpoint_path,
            metrics={"test_accuracy": test_metrics["accuracy"]},
            description="Vietnamese intent classifier trained on project-authored data",
        )

        registry.record_evaluation(
            model_version=model_version,
            result={
                "task": "intent_classification",
                "accuracy": test_metrics["accuracy"],
                "correct": test_metrics["correct"],
                "total": test_metrics["total"],
            },
        )

        return result

    except Exception as error:
        try:
            registry.fail_run(
                run_id=run.run_id,
                error=f"{type(error).__name__}: {error}",
            )
        except ValueError:
            pass
        raise


if __name__ == "__main__":
    print(json.dumps(run_training(), ensure_ascii=False, indent=2))
    