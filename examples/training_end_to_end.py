"""Runnable end-to-end training example using ProjectAI's self-built engine."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from data.dataset.dataset import DatasetRecord, TrainingDataset
from evaluation.dataset_evaluator import evaluate_dataset
from self_built.layers import Linear
from self_built.losses import MSELoss
from self_built.model import Model
from self_built.network import Sequential
from self_built.optimizers import SGD
from self_built.tensor import Tensor
from training.checkpoint import CheckpointManager
from training.configuration import TrainingConfiguration
from training.execution import TrainingExecutor
from training.loop import TrainingLoop
from training.model_loader import ModelLoader
from training.registry import TrainingRegistry


def make_dataset() -> TrainingDataset:
    """Create deterministic synthetic data for the training smoke test."""

    records = []

    for index in range(100):
        x = -1.0 + (2.0 * index / 99)
        y = 2.0 * x + 1.0

        records.append(
            DatasetRecord(
                record_id=f"synthetic-{index:03d}",
                input=str(x),
                output=str(y),
                metadata={
                    "source": "synthetic",
                    "task": "linear_regression",
                },
            )
        )

    return TrainingDataset(
        name="linear-regression-smoke-test",
        version="1.0.0",
        dataset_type="instruction",
        records=records,
        metadata={
            "description": "Deterministic numeric training smoke test",
            "synthetic": True,
        },
    )


def split_dataset(
    dataset: TrainingDataset,
) -> tuple[TrainingDataset, TrainingDataset, TrainingDataset]:
    """Split records into train, validation, and test sets."""

    records = dataset.records

    return (
        TrainingDataset(
            name=dataset.name,
            version=dataset.version,
            dataset_type=dataset.dataset_type,
            records=records[:70],
            metadata={"split": "train"},
        ),
        TrainingDataset(
            name=dataset.name,
            version=dataset.version,
            dataset_type=dataset.dataset_type,
            records=records[70:85],
            metadata={"split": "validation"},
        ),
        TrainingDataset(
            name=dataset.name,
            version=dataset.version,
            dataset_type=dataset.dataset_type,
            records=records[85:],
            metadata={"split": "test"},
        ),
    )


def encode_batch(batch) -> tuple[Tensor, Tensor]:
    """Encode numeric strings into model input and target tensors."""

    inputs = Tensor(
        [[float(value)] for value in batch.inputs]
    )
    targets = Tensor(
        [[float(value)] for value in batch.outputs]
    )

    return inputs, targets


def build_model(learning_rate: float) -> Model:
    """Build a trainable linear model with the self-built engine."""

    network = Sequential(
        Linear(
            in_features=1,
            out_features=1,
            seed=42,
        )
    )

    optimizer = SGD(
        parameters=network.parameters(),
        learning_rate=learning_rate,
    )

    return Model(
        network=network,
        loss=MSELoss(),
        optimizer=optimizer,
    )


def run_training_demo(
    output_dir: str | Path,
) -> dict[str, Any]:
    """Run training, validation, checkpointing, registry, and test evaluation."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset = make_dataset()
    train_dataset, validation_dataset, test_dataset = split_dataset(dataset)

    configuration = TrainingConfiguration(
        epochs=100,
        learning_rate=0.03,
        seed=42,
        batch_size=8,
        shuffle=True,
        gradient_accumulation_steps=1,
        mixed_precision=False,
        num_workers=0,
        dataset_name=train_dataset.name,
        dataset_version=train_dataset.version,
        dataset_type=train_dataset.dataset_type,
    )
    configuration.validate()

    registry = TrainingRegistry(output_dir / "registry.json")
    checkpoint_manager = CheckpointManager(
        output_dir / "checkpoints"
    )

    model = build_model(configuration.learning_rate)

    training_loop = TrainingLoop(
        model=model,
        checkpoint_manager=checkpoint_manager,
        configuration=configuration,
    )

    executor = TrainingExecutor(
        training_loop=training_loop,
        dataset=train_dataset,
        batch_encoder=encode_batch,
        validation_dataset=validation_dataset,
        validation_encoder=encode_batch,
        early_stopping_patience=15,
        min_delta=1e-8,
    )

    run = registry.create_run(
        configuration=configuration.to_dict(),
        dataset={
            "name": train_dataset.name,
            "version": train_dataset.version,
            "dataset_type": train_dataset.dataset_type,
            "train_records": len(train_dataset),
            "validation_records": len(validation_dataset),
            "test_records": len(test_dataset),
            "source": "synthetic",
        },
    )

    try:
        history = executor.run()

        if history.stopped_safely:
            raise RuntimeError(
                "Training stopped by Resource Guard: "
                f"{history.stop_reason}"
            )

        if history.checkpoint_path is None:
            raise RuntimeError(
                "Training completed without a best checkpoint. "
                "Validation should have produced one."
            )

        if not Path(history.checkpoint_path).exists():
            raise FileNotFoundError(history.checkpoint_path)

        registry.complete_run(
            run_id=run.run_id,
            metrics={
                "best_epoch": history.best_epoch,
                "best_validation_loss": history.best_validation_loss,
                "final_training_loss": (
                    history.epoch_metrics[-1]["training_loss"]
                ),
                "epochs_completed": len(history.epoch_metrics),
            },
            checkpoint_path=history.checkpoint_path,
        )

        model_version = f"demo-{run.run_id}"

        registry.register_model(
            model_version=model_version,
            run_id=run.run_id,
            checkpoint_path=history.checkpoint_path,
            metrics={
                "best_validation_loss": history.best_validation_loss,
            },
            description="End-to-end synthetic regression training demo",
        )

        loader = ModelLoader(
            registry=registry,
            checkpoint_manager=checkpoint_manager,
        )
        best_model = loader.load_model(model_version)

        evaluation_result = evaluate_dataset(
            model=best_model,
            dataset=test_dataset,
            batch_encoder=encode_batch,
            batch_size=configuration.batch_size,
        )

        saved_evaluation = registry.record_evaluation(
            model_version=model_version,
            result=asdict(evaluation_result),
        )

        first_epoch_loss = history.epoch_metrics[0]["training_loss"]
        last_epoch_loss = history.epoch_metrics[-1]["training_loss"]

        result = {
            "run_id": run.run_id,
            "model_version": model_version,
            "evaluation_id": saved_evaluation.evaluation_id,
            "epochs_completed": len(history.epoch_metrics),
            "best_epoch": history.best_epoch,
            "first_epoch_training_loss": first_epoch_loss,
            "last_epoch_training_loss": last_epoch_loss,
            "best_validation_loss": history.best_validation_loss,
            "test_loss": evaluation_result.loss,
            "test_mae": evaluation_result.mae,
            "test_mse": evaluation_result.mse,
            "checkpoint_path": history.checkpoint_path,
            "registry_path": str(registry.path),
        }

        if not last_epoch_loss < first_epoch_loss:
            raise AssertionError(
                "Training loss did not decrease. "
                f"First={first_epoch_loss}, last={last_epoch_loss}"
            )

        if evaluation_result.mse >= 0.1:
            raise AssertionError(
                "Test MSE did not meet the smoke-test threshold: "
                f"{evaluation_result.mse}"
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
    result = run_training_demo("artifacts/training_demo")
    print(json.dumps(result, indent=2, ensure_ascii=False))