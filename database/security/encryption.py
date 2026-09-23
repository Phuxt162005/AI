"""Encryption policy and storage abstraction."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EncryptionPolicy:
    """Describe encryption requirements for protected data."""

    at_rest: bool = True
    in_transit: bool = True
    algorithm: str = "external-provider-required"

    def validate(self) -> None:
        """Validate that required protection is configured."""

        if not self.at_rest:
            raise ValueError("Encryption at rest must be enabled")

        if not self.in_transit:
            raise ValueError("Encryption in transit must be enabled")

        if not self.algorithm.strip():
            raise ValueError(
                "Encryption algorithm/provider must be specified"
            )

class EncryptionProvider:
    """Boundary for a real encryption implementation."""

    def __init__(self, policy: EncryptionPolicy) -> None:
        policy.validate()
        self.policy = policy

    def protect(self, data: bytes) -> bytes:
        """Protect data through an external encryption provider.

        This foundation intentionally does not implement a custom
        cryptographic algorithm.
        """

        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")

        raise NotImplementedError("Connect a vetted encryption provider here")

    def unprotect(self, data: bytes) -> bytes:
        """Decrypt data through an external encryption provider."""

        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")

        raise NotImplementedError("Connect a vetted encryption provider here")