"""ProjectAI custom exceptions."""


class ProjectAIError(Exception):
    """Base exception for ProjectAI."""


class ConfigurationError(ProjectAIError):
    """Raised when application configuration is invalid."""