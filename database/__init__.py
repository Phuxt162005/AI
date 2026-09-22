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

    MemoryRepository,

    DocumentRepository,
    DocumentVersionRepository,
    ChunkRepository,

    AgentConfigurationRepository,
    AgentExecutionRepository,
    AgentRepository,
    AgentTaskRepository,
    AgentToolRepository,
    ExecutionResultRepository,
    GoalRepository,
    PlanRepository,
    PlanStepRepository,
    ToolCallRepository,
    ToolRepository,

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
    # Database foundation
    "DatabaseConfig",
    "DatabaseConnection",
    "DataAccess",
    "BaseRepository",
    "EntityMapper",
    "Transaction",

    # Runtime data
    "UserRepository",
    "UserProfileRepository",
    "UserPreferenceRepository",
    "ConversationRepository",
    "MessageRepository",

    # Memory
    "MemoryRepository",

    # Knowledge / RAG
    "DocumentRepository",
    "DocumentVersionRepository",
    "ChunkRepository",

    # Agent / Tool
    "AgentConfigurationRepository",
    "AgentExecutionRepository",
    "AgentRepository",
    "AgentTaskRepository",
    "AgentToolRepository",
    "ExecutionResultRepository",
    "GoalRepository",
    "PlanRepository",
    "PlanStepRepository",
    "ToolCallRepository",
    "ToolRepository",

    # Model / Training / Evaluation
    "ModelRepository",
    "ModelVersionRepository",
    "DatasetRepository",
    "TrainingConfigurationRepository",
    "TrainingRunRepository",
    "EvaluationResultRepository",
    "ModelRegistryRepository",

    # Personality
    "PersonalityRepository",
    "EmotionRepository",
    "MoodRepository",
    "RelationshipRepository",

    # Avatar
    "AvatarRepository",
    "ExpressionRepository",
    "AnimationRepository",
    "VoiceRepository",
    "AudioRepository",
    "VisualStateRepository",
]