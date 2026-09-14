"""Avatar runtime orchestration.

The AvatarRuntime coordinates:

    Avatar
        ↓
    AnimationController
        ↓
    VTuberModel
        ↓
    AvatarRenderer

The runtime contains orchestration only. It does not perform AI
reasoning, emotion calculation, personality logic, or graphics work.
"""

from __future__ import annotations

from enum import Enum

from .animation import AnimationController, AnimationPlaybackState
from .avatar import Avatar
from .model import (
    ModelExpression,
    ModelPose,
    VTuberModel,
)
from .renderer import AvatarRenderer
from .state import (
    AvatarAction,
    AvatarActionType,
    AvatarState,
    AvatarVisibility,
)

class AvatarRuntimeState(str, Enum):
    """Lifecycle state of the Avatar runtime."""

    STOPPED = "stopped"
    RUNNING = "running"

class AvatarRuntime:
    """Coordinate Avatar state, animation, model, and renderer."""

    def __init__(
        self,
        avatar: Avatar,
        model: VTuberModel,
        renderer: AvatarRenderer,
        animation_controller: AnimationController | None = None,
    ) -> None:
        self._avatar = avatar
        self._model = model
        self._renderer = renderer
        self._animation = animation_controller or AnimationController()
        self._runtime_state = AvatarRuntimeState.STOPPED

    @property
    def avatar(self) -> Avatar:
        """Return the managed Avatar."""

        return self._avatar

    @property
    def model(self) -> VTuberModel:
        """Return the configured VTuber model."""

        return self._model

    @property
    def renderer(self) -> AvatarRenderer:
        """Return the configured renderer."""

        return self._renderer

    @property
    def animation_controller(self) -> AnimationController:
        """Return the animation controller."""

        return self._animation

    @property
    def state(self) -> AvatarRuntimeState:
        """Return the current runtime lifecycle state."""

        return self._runtime_state

    @property
    def is_running(self) -> bool:
        """Return whether the runtime is running."""

        return self._runtime_state is AvatarRuntimeState.RUNNING

    def start(self) -> None:
        """Start the Avatar runtime.

        The model is loaded first, followed by renderer initialization.
        If initialization fails, the runtime remains stopped and already
        initialized resources are cleaned up.
        """

        if self.is_running:
            return

        model_loaded_here = False
        renderer_initialized_here = False

        try:
            if not self._model.is_loaded:
                self._model.load()
                model_loaded_here = True

            if not self._renderer.is_initialized:
                self._renderer.initialize()
                renderer_initialized_here = True

            self._runtime_state = AvatarRuntimeState.RUNNING

            self._synchronize_model()

        except Exception:
            if renderer_initialized_here:
                self._renderer.shutdown()

            if model_loaded_here:
                self._model.unload()

            self._runtime_state = AvatarRuntimeState.STOPPED
            raise

    def stop(self) -> None:
        """Stop the Avatar runtime.

        Renderer shutdown happens before model unloading.
        """

        if not self.is_running:
            return

        try:
            if self._renderer.is_initialized:
                self._renderer.shutdown()
        finally:
            if self._model.is_loaded:
                self._model.unload()

            self._animation.reset()
            self._runtime_state = AvatarRuntimeState.STOPPED

    def apply(self, action: AvatarAction) -> AvatarState:
        """Apply an Avatar action and synchronize the runtime.

        The Avatar remains the source of high-level Avatar state.
        The animation controller receives the same action and the model
        receives the resulting state.
        """

        if not self.is_running:
            raise RuntimeError("Avatar runtime is not running.")

        state = self._avatar.apply(action)
        self._animation.submit_action(action)
        self._synchronize_model()

        return state

    def update(self, delta_time: float) -> None:
        """Advance animation state and synchronize the model.

        delta_time is supplied by the external application/runtime loop.
        This method does not create or own an FPS loop.
        """
        
        if delta_time < 0.0:
            raise ValueError("delta_time cannot be negative.")

        if not self.is_running:
            raise RuntimeError("Avatar runtime is not running.")

        self._animation.update(delta_time)
        self._synchronize_model()

    def render(self) -> None:
        """Render the current model state."""

        if not self.is_running:
            raise RuntimeError("Avatar runtime is not running.")
        if not self._renderer.is_initialized:
            raise RuntimeError("Avatar renderer is not initialized.")
        if not self._model.is_loaded:
            raise RuntimeError("VTuber model is not loaded.")
        self._renderer.render(self._model.snapshot)

    def reset(self) -> AvatarState:
        """Reset Avatar, animation, and model state."""

        if not self.is_running:
            raise RuntimeError("Avatar runtime is not running.")

        state = self._avatar.reset()
        self._animation.reset()
        self._model.reset()
        self._synchronize_model()
        return state

    def _synchronize_model(self) -> None:
        """Synchronize high-level Avatar state with the model."""

        if not self._model.is_loaded:
            raise RuntimeError("VTuber model is not loaded.")

        state = self._avatar.state
        self._model.set_expression(ModelExpression(state.expression.value))
        self._model.set_pose( ModelPose(state.pose.value))
        self._model.set_visibility(state.visibility is AvatarVisibility.VISIBLE)
        self._synchronize_parameters(state)

    def _synchronize_parameters(self, state: AvatarState) -> None:
        """Synchronize Avatar parameters supported by the model.

        Avatar parameters are normalized to [-1, 1]. They are translated
        into each model parameter's own range before being applied.

        Parameters that do not exist on a particular model are ignored,
        because Avatar parameters are intentionally model-independent.
        """

        parameters = self._model.get_parameters()

        for name, normalized_value in state.parameters.items():
            parameter = parameters.get(name)

            if parameter is None:
                continue
            model_value = self._map_parameter_value(
                normalized_value,
                parameter.minimum,
                parameter.maximum,
            )
            self._model.set_parameter(name, model_value)

    @staticmethod
    def _map_parameter_value(
        normalized_value: float,
        minimum: float,
        maximum: float,
    ) -> float:
        """Map an Avatar [-1, 1] value to a model parameter range."""

        normalized = max(-1.0, min(1.0, float(normalized_value)))
        if minimum == maximum:
            return minimum

        ratio = (normalized + 1.0) / 2.0
        return minimum + ratio * (maximum - minimum)