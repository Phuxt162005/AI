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
        
def test_rag_pipeline_runs_in_required_order():
    calls = []

    def stage(name):
        def execute(value):
            calls.append(name)
            return value + [name]

        return execute

    pipeline = (
        FinalDataPipeline.create_rag_pipeline(
            [
                PipelineStage(
                    name=name,
                    function=stage(name),
                )
                for name
                in FinalDataPipeline.RAG_STAGES
            ]
        )
    )

    result = pipeline.run_rag([])

    assert result.success

    assert result.completed_stages == list(
        FinalDataPipeline.RAG_STAGES
    )

    assert calls == list(
        FinalDataPipeline.RAG_STAGES
    )
    
def test_rag_pipeline_stops_on_failure():
    def fail(_):
        raise RuntimeError(
            "embedding failed"
        )

    stages = [
        PipelineStage(
            name="document",
            function=lambda value: value,
        ),
        PipelineStage(
            name="chunking",
            function=lambda value: value,
        ),
        PipelineStage(
            name="text_cleaning",
            function=lambda value: value,
        ),
        PipelineStage(
            name="embedding_model",
            function=fail,
        ),
        PipelineStage(
            name="embedding_vector",
            function=lambda value: value,
        ),
        PipelineStage(
            name="vector_database",
            function=lambda value: value,
        ),
    ]

    pipeline = (
        FinalDataPipeline.create_rag_pipeline(
            stages
        )
    )

    result = pipeline.run_rag("document")

    assert not result.success
    assert result.failed_stage == (
        "embedding_model"
    )

    assert "vector_database" not in (
        result.completed_stages
    )