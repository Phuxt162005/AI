"""Central logging configuration for ProjectAI."""

from __future__ import annotations

import logging


LOGGER_NAME = "projectai"


def configure_logging(level: str = "INFO") -> logging.Logger:
    """Configure and return the ProjectAI logger."""

    logger = logging.getLogger(LOGGER_NAME)

    numeric_level = getattr(logging, level.upper(), None)

    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid logging level: {level}")

    logger.setLevel(numeric_level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(levelname)s] projectai: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False

    logger.info("Logging configured.")

    return logger