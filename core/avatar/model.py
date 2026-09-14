"""Technology-independent VTuber model abstraction.

This module defines the interface between the Avatar system and a
concrete VTuber model implementation.

The core Avatar system does not know about Live2D, VRM, VTube Studio,
rendering frameworks, or graphics APIs. Concrete adapters implement
VTuberModel and translate these abstractions into technology-specific
operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

class ModelExpression(str, Enum):
    """Technology-independent model expressions."""

    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    CURIOUS = "curious"
    CONCERNED = "concerned"
    RELIEVED = "relieved"

class ModelPose(str, Enum):
    """Technology-independent model poses."""

    DEFAULT = "default"
    RELAXED = "relaxed"
    ATTENTIVE = "attentive"
    THINKING = "thinking"
    EXCITED = "excited"
    SAD = "sad"

@dataclass
class ModelParameter:
    """A technology-independent model parameter.

    A parameter has a bounded value and a default value.

    The parameter does not know how the underlying VTuber technology
    represents or applies that value.
    """

    name: str
    minimum: float
    maximum: float
    default: float
    value: float | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Model parameter name cannot be empty.")

        if self.minimum > self.maximum:
            raise ValueError("Parameter minimum cannot exceed maximum.")

        if not self.minimum <= self.default <= self.maximum:
            raise ValueError(
                f"Default value for parameter '{self.name}' "
                "must be within its range."
            )

        if self.value is None:
            self.value = self.default
        else:
            self.value = self._clamp(self.value)

    def _clamp(self, value: float) -> float:
        """Clamp a value to the parameter range."""

        return max(self.minimum, min(self.maximum, float(value)))

    def set_value(self, value: float) -> float:
        """Set and return the constrained parameter value."""

        self.value = self._clamp(value)
        return self.value

    def reset(self) -> float:
        """Reset the parameter to its default value."""

        self.value = self.default
        return self.value

@dataclass(frozen=True)
class ModelSnapshot:
    """Immutable snapshot of the current model state."""

    loaded: bool
    visible: bool
    expression: ModelExpression
    pose: ModelPose
    parameters: Mapping[str, float] = field(default_factory=dict)

class VTuberModel(ABC):
    """Abstract VTuber model interface.

    Concrete VTuber technologies must implement this interface.

    The interface intentionally contains no rendering API, graphics API,
    or technology-specific data.
    """

    @abstractmethod
    def load(self) -> None:
        """Load the model and make it available to the application."""

    @abstractmethod
    def unload(self) -> None:
        """Unload the model and release model resources."""

    @property
    @abstractmethod
    def is_loaded(self) -> bool:
        """Return whether the model is currently loaded."""

    @abstractmethod
    def get_parameters(self) -> Mapping[str, ModelParameter]:
        """Return the model's available parameters."""

    @abstractmethod
    def get_parameter(self, name: str) -> ModelParameter | None:
        """Return a parameter by name, or None if it does not exist."""

    @abstractmethod
    def set_parameter(self, name: str, value: float) -> None:
        """Set a model parameter."""

    @abstractmethod
    def set_expression(self, expression: ModelExpression) -> None:
        """Set the current model expression."""

    @abstractmethod
    def set_pose(self, pose: ModelPose) -> None:
        """Set the current model pose."""

    @abstractmethod
    def set_visibility(self, visible: bool) -> None:
        """Set model visibility."""

    @abstractmethod
    def reset(self) -> None:
        """Reset model state to its default state."""

    @property
    @abstractmethod
    def snapshot(self) -> ModelSnapshot:
        """Return an immutable snapshot of the current model state."""

class MockVTuberModel(VTuberModel):
    """In-memory VTuber model used for testing.

    This class performs no rendering and has no dependency on any
    VTuber SDK. It simply stores model state in memory.
    """

    DEFAULT_PARAMETERS = (
        ("mouth_open", -1.0, 1.0, 0.0),
        ("eye_open", -1.0, 1.0, 0.0),
        ("eyebrow", -1.0, 1.0, 0.0),
        ("head_x", -1.0, 1.0, 0.0),
        ("head_y", -1.0, 1.0, 0.0),
        ("body_angle", -1.0, 1.0, 0.0),
    )

    def __init__(
        self,
        parameters: Mapping[str, ModelParameter] | None = None,
    ) -> None:
        self._loaded = False
        self._visible = True
        self._expression = ModelExpression.NEUTRAL
        self._pose = ModelPose.DEFAULT

        if parameters is None:
            self._parameters = {
                name: ModelParameter(
                    name=name,
                    minimum=minimum,
                    maximum=maximum,
                    default=default,
                )
                for name, minimum, maximum, default in self.DEFAULT_PARAMETERS
            }
        else:
            self._parameters = {
                name: ModelParameter(
                    name=parameter.name,
                    minimum=parameter.minimum,
                    maximum=parameter.maximum,
                    default=parameter.default,
                    value=parameter.value,
                )
                for name, parameter in parameters.items()
            }

    def _require_loaded(self) -> None:
        """Ensure the model is loaded before changing model state."""

        if not self._loaded:
            raise RuntimeError("VTuber model is not loaded.")

    def load(self) -> None:
        """Load the mock model."""

        self._loaded = True

    def unload(self) -> None:
        """Unload the mock model."""

        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        """Return whether the mock model is loaded."""

        return self._loaded

    def get_parameters(self) -> Mapping[str, ModelParameter]:
        """Return the available model parameters."""

        return dict(self._parameters)

    def get_parameter(self, name: str) -> ModelParameter | None:
        """Return a model parameter by name."""

        return self._parameters.get(name)

    def set_parameter(self, name: str, value: float) -> None:
        """Set a model parameter.

        The value is constrained to the parameter's configured range.
        """

        self._require_loaded()
        parameter = self._parameters.get(name)
        if parameter is None:
            raise KeyError(f"Unknown model parameter: '{name}'.")
        parameter.set_value(value)

    def set_expression(self, expression: ModelExpression) -> None:
        """Set the model expression."""

        self._require_loaded()

        if not isinstance(expression, ModelExpression):
            raise TypeError("expression must be a ModelExpression.")

        self._expression = expression

    def set_pose(self, pose: ModelPose) -> None:
        """Set the model pose."""

        self._require_loaded()

        if not isinstance(pose, ModelPose):
            raise TypeError("pose must be a ModelPose.")

        self._pose = pose

    def set_visibility(self, visible: bool) -> None:
        """Set model visibility."""

        self._require_loaded()

        if not isinstance(visible, bool):
            raise TypeError("visible must be a boolean.")

        self._visible = visible

    def reset(self) -> None:
        """Reset all model state to its defaults."""

        self._require_loaded()

        self._expression = ModelExpression.NEUTRAL
        self._pose = ModelPose.DEFAULT
        self._visible = True

        for parameter in self._parameters.values():
            parameter.reset()

    @property
    def snapshot(self) -> ModelSnapshot:
        """Return an immutable snapshot of the current model state."""

        return ModelSnapshot(
            loaded=self._loaded,
            visible=self._visible,
            expression=self._expression,
            pose=self._pose,
            parameters={
                name: float(parameter.value)
                for name, parameter in self._parameters.items()
            },
        )