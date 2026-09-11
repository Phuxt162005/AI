"""Tool registry for ProjectAI."""

from __future__ import annotations

from core.interfaces import ToolInterface


class ToolRegistry:
    """Registry that manages available Agent tools."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolInterface] = {}

    def register(self, tool: ToolInterface) -> None:
        """Register a tool."""

        if not isinstance(tool, ToolInterface):
            raise TypeError("tool must implement ToolInterface.")
        
        name = tool.name.strip()
        if not name:
            raise ValueError("Tool name must not be empty.")
        if name in self._tools:
            raise ValueError(f"Tool '{name}' is already registered.")
        self._tools[name] = tool

    def unregister(self, name: str) -> None:
        """Remove a registered tool."""

        normalized_name = self._normalize_name(name)
        if normalized_name not in self._tools:
            raise KeyError(f"Tool '{normalized_name}' is not registered.")

        del self._tools[normalized_name]

    def get(self, name: str) -> ToolInterface:
        """Return a registered tool by name."""

        normalized_name = self._normalize_name(name)
        try:
            return self._tools[normalized_name]
        except KeyError as exc:
            raise KeyError(
                f"Tool '{normalized_name}' is not registered."
            ) from exc

    def has(self, name: str) -> bool:
        """Return whether a tool is registered."""

        normalized_name = self._normalize_name(name)
        return normalized_name in self._tools

    def list(self) -> list[str]:
        """Return registered tool names."""

        return list(self._tools.keys())

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Validate and normalize a tool name."""

        if not isinstance(name, str):
            raise TypeError("Tool name must be a string.")

        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Tool name must not be empty.")

        return normalized_name