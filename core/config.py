"""ProjectAI configuration management."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.exceptions import ConfigurationError


@dataclass(frozen=True)
class AppConfig:
    """Application configuration."""

    name: str = "ProjectAI"
    version: str = "0.1.0"
    log_level: str = "INFO"
    model_dir: str = "models"
    data_dir: str = "data"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfig":
        """Create configuration from a dictionary."""

        if not isinstance(data, dict):
            raise ConfigurationError("Configuration root must be an object.")

        name = data.get("name", cls.name)
        version = data.get("version", cls.version)
        log_level = data.get("log_level", cls.log_level)
        model_dir = data.get("model_dir", cls.model_dir)
        data_dir = data.get("data_dir", cls.data_dir)

        if not isinstance(name, str) or not name.strip():
            raise ConfigurationError("Configuration 'name' must be a non-empty string.")

        if not isinstance(version, str) or not version.strip():
            raise ConfigurationError(
                "Configuration 'version' must be a non-empty string."
            )

        return cls(
            name=name,
            version=version,
            log_level=log_level,
            model_dir=model_dir,
            data_dir=data_dir,
        )

    @classmethod
    def load(cls, path: str | Path) -> "AppConfig":
        """Load configuration from a JSON file."""

        config_path = Path(path)

        if not config_path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {config_path}"
            )

        try:
            with config_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise ConfigurationError(
                f"Invalid JSON configuration: {config_path}"
            ) from exc
        except OSError as exc:
            raise ConfigurationError(
                f"Unable to read configuration: {config_path}"
            ) from exc

        return cls.from_dict(data)