import pytest

from data.dataset.dataset import DatasetRecord, TrainingDataset
from evaluation.dataset_evaluator import evaluate_dataset
from self_built.tensor import Tensor


class FakeLoss:
    def forward(self, predictions, targets):
        if predictions.shape != targets.shape:
            raise ValueError("Shape mismatch.")

        return sum(
            (float(prediction) - float(target)) ** 2
            for prediction, target in zip(
                predictions._data,
                targets._data,
            )
        ) / predictions.size


class FakeModel:
    def __init__(self):
        self.loss = FakeLoss()
        self.eval_calls = 0
        self.predict_calls = 0

    def eval(self):
        self.eval_calls += 1

    def predict(self, inputs):
        self.predict_calls += 1
        return inputs


def make_dataset(values):
    return TrainingDataset(
        name="evaluation-test",
        version="1.0",
        dataset_type="instruction",
        records=[
            DatasetRecord(
                record_id=f"record-{index}",
                input=str(value),
                output=str(value),
            )
            for index, value in enumerate(values)
        ],
    )


def encode_batch(batch):
    inputs = Tensor([[float(value)] for value in batch.inputs])
    targets = Tensor([[float(value) + 1.0] for value in batch.outputs])
    return inputs, targets


def test_evaluate_dataset_returns_aggregated_metrics():
    model = FakeModel()
    dataset = make_dataset([1, 2, 3])

    result = evaluate_dataset(
        model=model,
        dataset=dataset,
        batch_encoder=encode_batch,
        batch_size=2,
    )

    assert result.dataset_name == "evaluation-test"
    assert result.dataset_version == "1.0"
    assert result.dataset_type == "instruction"
    assert result.evaluated_records == 3
    assert result.batch_count == 2
    assert result.loss == pytest.approx(1.0)
    assert result.mae == pytest.approx(1.0)
    assert result.mse == pytest.approx(1.0)


def test_evaluation_sets_model_to_eval_mode():
    model = FakeModel()

    evaluate_dataset(
        model=model,
        dataset=make_dataset([1, 2]),
        batch_encoder=encode_batch,
    )

    assert model.eval_calls == 1


def test_evaluation_does_not_call_optimizer_or_training():
    model = FakeModel()

    evaluate_dataset(
        model=model,
        dataset=make_dataset([1, 2]),
        batch_encoder=encode_batch,
    )

    assert not hasattr(model, "optimizer")
    assert not hasattr(model, "train")


def test_evaluation_rejects_empty_dataset():
    with pytest.raises(ValueError, match="must not be empty"):
        evaluate_dataset(
            model=FakeModel(),
            dataset=make_dataset([]),
            batch_encoder=encode_batch,
        )


def test_evaluation_rejects_invalid_batch_size():
    with pytest.raises(ValueError, match="batch_size"):
        evaluate_dataset(
            model=FakeModel(),
            dataset=make_dataset([1]),
            batch_encoder=encode_batch,
            batch_size=0,
        )


def test_evaluation_rejects_non_tensor_encoder_output():
    with pytest.raises(TypeError, match="Tensor inputs"):
        evaluate_dataset(
            model=FakeModel(),
            dataset=make_dataset([1]),
            batch_encoder=lambda batch: (["not a tensor"], Tensor([[1.0]])),
        )


def test_evaluation_rejects_prediction_target_shape_mismatch():
    class MismatchedModel(FakeModel):
        def predict(self, inputs):
            return Tensor([[1.0], [2.0]])

    with pytest.raises(ValueError, match="shapes must match"):
        evaluate_dataset(
            model=MismatchedModel(),
            dataset=make_dataset([1]),
            batch_encoder=encode_batch,
        )