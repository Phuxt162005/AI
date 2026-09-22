import pytest

from core.knowledge.access_control import (
    KnowledgeAccessController,
)


def test_build_filter():
    controller = KnowledgeAccessController()

    result = controller.build_filter(
        user_id=10,
    )

    assert result == {
        "user_id": 10,
    }


def test_authorize_matching_user():
    controller = KnowledgeAccessController()

    assert controller.authorize(
        user_id=10,
        metadata={
            "user_id": 10,
        },
    )


def test_reject_different_user():
    controller = KnowledgeAccessController()

    assert not controller.authorize(
        user_id=10,
        metadata={
            "user_id": 20,
        },
    )


def test_public_knowledge():
    controller = KnowledgeAccessController()

    assert controller.authorize(
        user_id=10,
        metadata={},
    )


def test_invalid_user():
    controller = KnowledgeAccessController()

    with pytest.raises(ValueError):
        controller.build_filter(0)