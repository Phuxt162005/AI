"""Encryption policy and storage abstraction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


EncryptFunction = Callable[[bytes], bytes]
DecryptFunction = Callable[[bytes], bytes]


@dataclass(frozen=True)
class EncryptionPolicy:
    """Describe encryption requirements for protected data."""

    at_rest: bool = True
    in_transit: bool = True
    algorithm: str = "external-provider-required"

    def validate(self) -> None:
        """Validate that required protection is configured."""

        if not self.at_rest:
            raise ValueError(
                "Encryption at rest must be enabled"
            )

        if not self.in_transit:
            raise ValueError(
                "Encryption in transit must be enabled"
            )

        if not self.algorithm.strip():
            raise ValueError(
                "Encryption algorithm/provider must be specified"
            )


class EncryptionProvider:
    """Encryption boundary using injected cryptographic functions."""

    def __init__(
        self,
        policy: EncryptionPolicy,
        encrypt: EncryptFunction | None = None,
        decrypt: DecryptFunction | None = None,
    ) -> None:
        policy.validate()

        if (encrypt is None) != (decrypt is None):
            raise ValueError(
                "encrypt and decrypt must be provided together"
            )

        self.policy = policy
        self._encrypt = encrypt
        self._decrypt = decrypt

    @property
    def configured(self) -> bool:
        """Return whether a real encryption provider is configured."""

        return (
            self._encrypt is not None
            and self._decrypt is not None
        )

    def protect(self, data: bytes) -> bytes:
        """Encrypt data using the configured provider."""

        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")

        if self._encrypt is None:
            raise RuntimeError(
                "No encryption provider is configured"
            )

        return self._encrypt(data)

    def unprotect(self, data: bytes) -> bytes:
        """Decrypt data using the configured provider."""

        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")

        if self._decrypt is None:
            raise RuntimeError(
                "No encryption provider is configured"
            )

        return self._decrypt(data)