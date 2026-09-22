"""Database foundation for ProjectAI."""

from database.access import (
    BaseRepository,
    DataAccess,
    EntityMapper,
    Transaction,
)
from database.config import DatabaseConfig
from database.connection import DatabaseConnection
from database.repositories import (
    UserRepository,
    UserProfileRepository,
    UserPreferenceRepository,
    ConversationRepository,
    MessageRepository,
)
from database.repositories import (
    ModelRepository,
    ModelVersionRepository,
    DatasetRepository,
    TrainingConfigurationRepository,
    TrainingRunRepository,
    EvaluationResultRepository,
    ModelRegistryRepository,
    PersonalityRepository,
    EmotionRepository,
    MoodRepository,
    RelationshipRepository,
    AvatarRepository,
    ExpressionRepository,
    AnimationRepository,
    VoiceRepository,
    AudioRepository,
    VisualStateRepository,
)

__all__ = [
    "DatabaseConfig",
    "DatabaseConnection",
    "DataAccess",
    "BaseRepository",
    "EntityMapper",
    "Transaction",
    "UserRepository",
    "UserProfileRepository",
    "UserPreferenceRepository",
    "ConversationRepository",
    "MessageRepository",
]

