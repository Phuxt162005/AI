"""Minimal configuration loader using only the Python standard library."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .exceptions import ConfigurationError


@dataclass(frozen=True)
class AppConfig:
    """Application configuration loaded from a JSON file."""

    name: str = "ProjectAI"
    version: str = "0.1.0"
    log_level: str = "INFO"
    model_dir: str = "models"
    data_dir: str = "data"

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> "AppConfig":
        """Create and validate configuration from a dictionary."""

        if not isinstance(values, dict):
            raise ConfigurationError(
                "Configuration root must be an object."
            )

        config = cls(
            name=values.get("name", cls.name),
            version=values.get("version", cls.version),
            log_level=values.get("log_level", cls.log_level),
            model_dir=values.get("model_dir", cls.model_dir),
            data_dir=values.get("data_dir", cls.data_dir),
        )

        if not isinstance(config.name, str) or not config.name.strip():
            raise ConfigurationError(
                "Configuration 'name' must be a non-empty string."
            )

        if not isinstance(config.version, str) or not config.version.strip():
            raise ConfigurationError(
                "Configuration 'version' must be a non-empty string."
            )

        if not isinstance(config.log_level, str):
            raise ConfigurationError(
                "Configuration 'log_level' must be a string."
            )

        if config.log_level.upper() not in {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }:
            raise ConfigurationError(
                f"Unsupported logging level: {config.log_level}"
            )

        if not isinstance(config.model_dir, str) or not config.model_dir.strip():
            raise ConfigurationError(
                "Configuration 'model_dir' must be a non-empty string."
            )

        if not isinstance(config.data_dir, str) or not config.data_dir.strip():
            raise ConfigurationError(
                "Configuration 'data_dir' must be a non-empty string."
            )

        return config

    @classmethod
    def load(cls, path: str | Path) -> "AppConfig":
        """Load configuration from a JSON file."""

        config_path = Path(path)

        if not config_path.is_file():
            raise ConfigurationError(
                f"Configuration file not found: {config_path}"
            )

        try:
            with config_path.open("r", encoding="utf-8") as file:
                values = json.load(file)
        except json.JSONDecodeError as exc:
            raise ConfigurationError(
                f"Invalid JSON configuration: {config_path}"
            ) from exc
        except OSError as exc:
            raise ConfigurationError(
                f"Unable to read configuration: {config_path}"
            ) from exc

        return cls.from_dict(values)