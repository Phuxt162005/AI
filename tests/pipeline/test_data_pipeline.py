import pytest

from pipeline.data_pipeline import (
    FinalDataPipeline,
    PipelineStage,
)


def test_final_pipeline_runs_in_required_order():
    calls = []

    def stage(name):
        def execute(value):
            calls.append(name)
            return value + [name]

        return execute

    pipeline = FinalDataPipeline(
        [
            PipelineStage(
                name=name,
                function=stage(name),
            )
            for name in FinalDataPipeline.REQUIRED_STAGES
        ]
    )

    result = pipeline.run([])

    assert result.success
    assert result.completed_stages == list(
        FinalDataPipeline.REQUIRED_STAGES
    )
    assert calls == list(
        FinalDataPipeline.REQUIRED_STAGES
    )


def test_final_pipeline_stops_on_failure():
    def fail(_):
        raise RuntimeError("training failed")

    stages = [
        PipelineStage(
            name="source",
            function=lambda value: value,
        ),
        PipelineStage(
            name="collection",
            function=lambda value: value,
        ),
        PipelineStage(
            name="validation",
            function=lambda value: value,
        ),
        PipelineStage(
            name="cleaning",
            function=lambda value: value,
        ),
        PipelineStage(
            name="preprocessing",
            function=lambda value: value,
        ),
        PipelineStage(
            name="storage",
            function=lambda value: value,
        ),
        PipelineStage(
            name="dataset",
            function=lambda value: value,
        ),
        PipelineStage(
            name="training",
            function=fail,
        ),
        PipelineStage(
            name="evaluation",
            function=lambda value: value,
        ),
    ]

    pipeline = FinalDataPipeline(stages)

    result = pipeline.run("data")

    assert not result.success
    assert result.failed_stage == "training"
    assert "dataset" in result.completed_stages
    assert "evaluation" not in result.completed_stages


def test_final_pipeline_rejects_wrong_order():
    with pytest.raises(ValueError):
        FinalDataPipeline(
            [
                PipelineStage(
                    name="training",
                    function=lambda value: value,
                )
            ]
        )