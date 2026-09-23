"""Authentication primitives."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass

@dataclass(frozen=True)
class PasswordHash:
    """Store password hashing parameters."""

    algorithm: str
    salt: str
    digest: str
    iterations: int

class PasswordHasher:
    """Hash and verify passwords using PBKDF2-HMAC."""

    ALGORITHM = "pbkdf2_sha256"
    DEFAULT_ITERATIONS = 600_000

    def __init__(self, iterations: int = DEFAULT_ITERATIONS) -> None:
        if iterations <= 0:
            raise ValueError("iterations must be > 0")

        self.iterations = iterations

    def hash_password(self, password: str) -> PasswordHash:
        """Create a password hash."""

        if not password:
            raise ValueError("password must not be empty")

        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            self.iterations,
        )

        return PasswordHash(
            algorithm=self.ALGORITHM,
            salt=salt.hex(),
            digest=digest.hex(),
            iterations=self.iterations,
        )

    def verify(
        self,
        password: str,
        password_hash: PasswordHash,
    ) -> bool:
        """Verify a password against its stored hash."""

        if not password:
            return False

        if password_hash.algorithm != self.ALGORITHM:
            return False

        try:
            salt = bytes.fromhex(password_hash.salt)
            expected = bytes.fromhex(password_hash.digest)
        except ValueError:
            return False

        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            password_hash.iterations,
        )

        return hmac.compare_digest(actual, expected)