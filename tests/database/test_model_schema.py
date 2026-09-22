from database.schema.model_schema import (
    MODEL_TABLES_DOWN_SQL,
    MODEL_TABLES_UP_SQL,
)


def test_model_schema_contains_required_tables():
    required = [
        "models",
        "training_datasets",
        "training_configurations",
        "training_runs",
        "model_versions",
        "evaluation_results",
        "model_registry",
    ]

    for table in required:
        assert f"`{table}`" in MODEL_TABLES_UP_SQL


def test_model_schema_has_foreign_keys():
    assert "FOREIGN KEY" in MODEL_TABLES_UP_SQL
    assert "model_versions" in MODEL_TABLES_UP_SQL
    assert "evaluation_results" in MODEL_TABLES_UP_SQL


def test_model_schema_down_order():
    assert (
        MODEL_TABLES_DOWN_SQL.index(
            "model_registry"
        )
        <
        MODEL_TABLES_DOWN_SQL.index(
            "models"
        )
    )