"""Technology-independent Avatar renderer abstraction.

This module defines the boundary between Avatar runtime state and
a concrete rendering implementation.

No graphics framework, window system, VTuber SDK, or rendering API
is used here.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import ModelSnapshot

class AvatarRenderer(ABC):
    """Abstract interface for rendering an Avatar model."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the renderer."""

    @abstractmethod
    def shutdown(self) -> None:
        """Shut down the renderer."""

    @property
    @abstractmethod
    def is_initialized(self) -> bool:
        """Return whether the renderer is initialized."""

    @abstractmethod
    def render(self, model: ModelSnapshot) -> None:
        """Render the supplied model state."""

@dataclass
class MockAvatarRenderer(AvatarRenderer):
    """In-memory renderer used for testing.

    This renderer performs no graphical rendering and does not create
    windows or depend on a graphics framework.
    """

    _initialized: bool = False
    _render_count: int = 0
    _last_rendered_model: ModelSnapshot | None = None

    def initialize(self) -> None:
        """Initialize the mock renderer."""

        self._initialized = True
        self._render_count = 0
        self._last_rendered_model = None

    def shutdown(self) -> None:
        """Shut down the mock renderer."""

        self._initialized = False

    @property
    def is_initialized(self) -> bool:
        """Return whether the renderer is initialized."""

        return self._initialized

    def render(self, model: ModelSnapshot) -> None:
        """Record the model state that would have been rendered."""

        if not self._initialized:
            raise RuntimeError("Avatar renderer is not initialized.")

        self._last_rendered_model = model
        self._render_count += 1

    @property
    def render_count(self) -> int:
        """Return the number of render calls."""

        return self._render_count

    @property
    def last_rendered_model(self) -> ModelSnapshot | None:
        """Return the most recently rendered model snapshot."""

        return self._last_rendered_model