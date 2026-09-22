"""Migration for Model, Training, Personality and Avatar data."""

from database.schema.avatar_schema import (
    AVATAR_TABLES_DOWN_SQL,
    AVATAR_TABLES_UP_SQL,
)
from database.schema.model_schema import (
    MODEL_TABLES_DOWN_SQL,
    MODEL_TABLES_UP_SQL,
)
from database.schema.personality_schema import (
    PERSONALITY_TABLES_DOWN_SQL,
    PERSONALITY_TABLES_UP_SQL,
)

V006_VERSION = 6
V006_NAME = "model_training_personality_avatar"

UP_SQL = "\n\n".join(
    [
        MODEL_TABLES_UP_SQL,
        PERSONALITY_TABLES_UP_SQL,
        AVATAR_TABLES_UP_SQL,
    ]
)

DOWN_SQL = "\n\n".join(
    [
        AVATAR_TABLES_DOWN_SQL,
        PERSONALITY_TABLES_DOWN_SQL,
        MODEL_TABLES_DOWN_SQL,
    ]
)