"""Database migrations."""

from database.migrations.migration import Migration
from database.migrations.runner import MigrationRunner
from database.migrations.v002_runtime_data import (
    DOWN_SQL,
    UP_SQL,
    V002_NAME,
    V002_VERSION,
)
from database.migrations.v003_memory import (
    DOWN_SQL as V003_DOWN_SQL,
    UP_SQL as V003_UP_SQL,
    V003_NAME,
    V003_VERSION,
)
from database.migrations.v004_knowledge import (
    DOWN_SQL as V004_DOWN_SQL,
    UP_SQL as V004_UP_SQL,
    V004_NAME,
    V004_VERSION,
)
from database.migrations.v005_agent import (
    DOWN_SQL as V005_DOWN_SQL,
    UP_SQL as V005_UP_SQL,
    V005_NAME,
    V005_VERSION,
)
from database.migrations.v006_model_personality_avatar import (
    V006_VERSION,
    V006_NAME,
    UP_SQL as V006_UP_SQL,
    DOWN_SQL as V006_DOWN_SQL,
)

__all__ = [
    "Migration",
    "MigrationRunner",
    "V002_VERSION",
    "V002_NAME",
    "UP_SQL",
    "DOWN_SQL",
    "V003_VERSION",
    "V003_NAME",
    "V003_UP_SQL",
    "V003_DOWN_SQL",
    "V004_VERSION",
    "V004_NAME",
    "V004_UP_SQL",
    "V004_DOWN_SQL",
    "V005_VERSION",
    "V005_NAME",
    "V005_UP_SQL",
    "V005_DOWN_SQL",
]