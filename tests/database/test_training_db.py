from database.models.evaluation import EvaluationResult
from database.models.model import (
    Model,
    ModelRegistry,
    ModelVersion,
    ModelVersionStatus,
)
from database.models.training_run import (
    Dataset,
    TrainingConfiguration,
    TrainingRun,
)


def test_model_entities():
    model = Model(
        model_id=None,
        name="assistant-model",
        model_type="language",
        framework="custom",
    )

    version = ModelVersion(
        model_version_id=None,
        model_id=1,
        version="1.0.0",
        status=ModelVersionStatus.TESTING,
        training_run_id=10,
    )

    registry = ModelRegistry(
        registry_id=None,
        model_version_id=1,
        environment="staging",
    )

    assert model.name == "assistant-model"
    assert version.version == "1.0.0"
    assert registry.environment == "staging"


def test_training_entities():
    dataset = Dataset(
        dataset_id=None,
        name="assistant-dataset",
        version="1.0",
        storage_reference="data/dataset/1.0",
    )

    configuration = TrainingConfiguration(
        configuration_id=None,
        version="config-1",
        parameters={
            "epochs": 5,
            "batch_size": 32,
        },
    )

    run = TrainingRun(
        training_run_id=None,
        dataset_id=1,
        configuration_id=1,
    )

    assert dataset.version == "1.0"
    assert configuration.parameters["epochs"] == 5
    assert run.dataset_id == 1


def test_evaluation_result():
    result = EvaluationResult(
        evaluation_id=None,
        model_version_id=1,
        metric_name="accuracy",
        metric_value=0.95,
    )

    assert result.metric_name == "accuracy"
    assert result.metric_value == 0.95