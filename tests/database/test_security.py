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