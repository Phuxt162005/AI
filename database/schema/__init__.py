"""Database schema definitions."""

from database.schema.base_schema import (
    DATABASE_NAME,
    create_database_sql,
)

from database.schema.memory_schema import (
    MEMORY_TABLE,
    MEMORY_TABLE_DROP_SQL,
    MEMORY_TABLE_SQL,
)

from database.schema.agent_schema import (
    AGENT_TABLES_DOWN_SQL,
    AGENT_TABLES_UP_SQL,
)

from database.schema.model_schema import (
    MODEL_TABLES_UP_SQL,
    MODEL_TABLES_DOWN_SQL,
)

from database.schema.personality_schema import (
    PERSONALITY_TABLES_UP_SQL,
    PERSONALITY_TABLES_DOWN_SQL,
)

from database.schema.avatar_schema import (
    AVATAR_TABLES_UP_SQL,
    AVATAR_TABLES_DOWN_SQL,
)

__all__ = [
    "DATABASE_NAME",
    "create_database_sql",

    "MEMORY_TABLE",
    "MEMORY_TABLE_SQL",
    "MEMORY_TABLE_DROP_SQL",

    "AGENT_TABLES_DOWN_SQL",
    "AGENT_TABLES_UP_SQL",

    "MODEL_TABLES_UP_SQL",
    "MODEL_TABLES_DOWN_SQL",

    "PERSONALITY_TABLES_UP_SQL",
    "PERSONALITY_TABLES_DOWN_SQL",

    "AVATAR_TABLES_UP_SQL",
    "AVATAR_TABLES_DOWN_SQL",
]