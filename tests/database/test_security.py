import pytest

from database.security.auth import PasswordHasher
from database.security.encryption import (
    EncryptionPolicy,
)
from database.security.privacy import (
    DataScope,
    PrivacyGuard,
)
from database.security.rbac import RBAC
from database.security.encryption import (
    EncryptionPolicy,
    EncryptionProvider,
)

def test_password_hash_and_verify():
    hasher = PasswordHasher(iterations=1000)

    password_hash = hasher.hash_password(
        "projectai-password"
    )

    assert hasher.verify(
        "projectai-password",
        password_hash,
    )

    assert not hasher.verify(
        "wrong-password",
        password_hash,
    )


def test_rbac_permission():
    rbac = RBAC()

    rbac.add_role(
        "admin",
        {"data.read", "data.delete"},
    )

    rbac.assign_role(
        "user-1",
        "admin",
    )

    assert rbac.has_permission(
        "user-1",
        "data.read",
    )

    assert not rbac.has_permission(
        "user-1",
        "data.export",
    )


def test_privacy_isolation():
    guard = PrivacyGuard()

    scope = DataScope(
        owner_id="user-1",
        visibility="private",
    )

    assert guard.can_access(
        "user-1",
        scope,
    )

    assert not guard.can_access(
        "user-2",
        scope,
    )

    with pytest.raises(PermissionError):
        guard.require_access(
            "user-2",
            scope,
        )


def test_encryption_policy_requires_protection():
    policy = EncryptionPolicy(
        at_rest=True,
        in_transit=True,
        algorithm="external-provider",
    )

    policy.validate()
    
def test_encryption_provider_with_injected_provider():
    def encrypt(data: bytes) -> bytes:
        return data[::-1]

    def decrypt(data: bytes) -> bytes:
        return data[::-1]

    provider = EncryptionProvider(
        policy=EncryptionPolicy(
            at_rest=True,
            in_transit=True,
            algorithm="test-provider",
        ),
        encrypt=encrypt,
        decrypt=decrypt,
    )
    original = b"ProjectAI"
    protected = provider.protect(original)

    assert protected != original
    assert provider.unprotect(protected) == original
    assert provider.configured
    
def test_encryption_provider_requires_configuration():
    provider = EncryptionProvider(
        EncryptionPolicy(
            at_rest=True,
            in_transit=True,
            algorithm="external-provider",
        )
    )

    assert not provider.configured

    with pytest.raises(RuntimeError):
        provider.protect(b"ProjectAI")