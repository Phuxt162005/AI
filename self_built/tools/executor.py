"""Tool execution component for ProjectAI."""

from __future__ import annotations

from typing import Any

from .registry import ToolRegistry

class ToolExecutionError(RuntimeError):
    """Raised when a registered tool fails during execution."""

class ToolExecutor:
    """Execute tools through a ToolRegistry."""

    def __init__(self, registry: ToolRegistry) -> None:
        if not isinstance(registry, ToolRegistry):
            raise TypeError("registry must be a ToolRegistry.")

        self._registry = registry

    @property
    def registry(self) -> ToolRegistry:
        """Return the underlying tool registry."""

        return self._registry

    def execute(
        self,
        tool_name: str,
        inputs: dict[str, Any],
    ) -> Any:
        """Execute a registered tool."""

        if not isinstance(inputs, dict):
            raise TypeError("Tool inputs must be a dictionary.")

        tool = self._registry.get(tool_name)

        try:
            return tool.execute(inputs)
        except Exception as exc:
            raise ToolExecutionError(
                f"Tool '{tool.name}' failed during execution."
            ) from exc