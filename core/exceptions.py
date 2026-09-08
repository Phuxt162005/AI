"""ProjectAI custom exceptions."""


class ProjectAIError(Exception):
    """Base exception for ProjectAI."""

class ConfigurationError(ProjectAIError):
    """Raised when application configuration is invalid."""

class ProjectAIError(Exception):
    """Base exception for the project."""


class ConfigurationError(ProjectAIError):
    """Raised when configuration is invalid."""


class InterfaceError(ProjectAIError):
    """Raised when a component violates an interface contract."""