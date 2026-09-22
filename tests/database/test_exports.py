from database import (
    AgentRepository,
    AvatarRepository,
    ModelRepository,
    PersonalityRepository,
)

from database.migrations import (
    V005_VERSION,
    V006_VERSION,
    V006_NAME,
    V006_UP_SQL,
    V006_DOWN_SQL,
)

from database.models import (
    Agent,
    Model,
    Personality,
    Avatar,
)

from database.schema import (
    MODEL_TABLES_UP_SQL,
    MODEL_TABLES_DOWN_SQL,
    PERSONALITY_TABLES_UP_SQL,
    PERSONALITY_TABLES_DOWN_SQL,
    AVATAR_TABLES_UP_SQL,
    AVATAR_TABLES_DOWN_SQL,
)


def test_database_repository_exports():
    assert AgentRepository is not None
    assert ModelRepository is not None
    assert PersonalityRepository is not None
    assert AvatarRepository is not None


def test_model_exports():
    assert Model is not None


def test_personality_exports():
    assert Personality is not None


def test_avatar_exports():
    assert Avatar is not None


def test_migration_exports():
    assert V005_VERSION == 5
    assert V006_VERSION == 6
    assert V006_NAME == "model_training_personality_avatar"
    assert V006_UP_SQL
    assert V006_DOWN_SQL


def test_schema_exports():
    assert MODEL_TABLES_UP_SQL
    assert MODEL_TABLES_DOWN_SQL

    assert PERSONALITY_TABLES_UP_SQL
    assert PERSONALITY_TABLES_DOWN_SQL

    assert AVATAR_TABLES_UP_SQL
    assert AVATAR_TABLES_DOWN_SQL