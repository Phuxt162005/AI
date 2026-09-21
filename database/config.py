"""Database configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass

@dataclass(frozen=True)
class DatabaseConfig:
    """Configuration required to connect to MySQL."""

    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = "projectai"
    charset: str = "utf8mb4"

    def __post_init__(self) -> None:
        if not self.host.strip():
            raise ValueError("host must not be empty")

        if not 1 <= self.port <= 65535:
            raise ValueError("port must be between 1 and 65535")

        if not self.user.strip():
            raise ValueError("user must not be empty")

        if not self.database.strip():
            raise ValueError("database must not be empty")

        if not self.charset.strip():
            raise ValueError("charset must not be empty")

    @classmethod
    def from_environment(cls) -> "DatabaseConfig":
        """Create configuration from environment variables."""

        return cls(
            host=os.getenv(
                "PROJECTAI_DB_HOST", "localhost"),
            port=int(os.getenv("PROJECTAI_DB_PORT", "3306")),
            user=os.getenv("PROJECTAI_DB_USER", "root"),
            password=os.getenv("PROJECTAI_DB_PASSWORD", ""),
            database=os.getenv("PROJECTAI_DB_NAME", "projectai"),
            charset=os.getenv("PROJECTAI_DB_CHARSET", "utf8mb4"),
        )

    def to_connection_dict(self) -> dict[str, object]:
        """Return connection parameters."""

        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.database,
            "charset": self.charset,
        }