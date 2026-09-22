import pytest

from core.agent_execution.tool_service import (
    ToolRegistry,
)


def test_register_and_get_tool():
    registry = ToolRegistry(
        tools={},
    )

    def search(data):
        return {
            "query": data["query"],
        }

    registry.register(
        tool_id=1,
        function=search,
    )

    result = registry.get(1)(
        {
            "query": "AI",
        }
    )

    assert result["query"] == "AI"


def test_unknown_tool():
    registry = ToolRegistry(
        tools={},
    )

    with pytest.raises(KeyError):
        registry.get(100)


def test_invalid_tool_id():
    registry = ToolRegistry(
        tools={},
    )

    with pytest.raises(ValueError):
        registry.register(
            tool_id=0,
            function=lambda data: data,
        )