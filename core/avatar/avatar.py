"""Technology-independent Avatar controller."""

from __future__ import annotations

from .state import (
    AvatarAction,
    AvatarActionType,
    AvatarActivity,
    AvatarExpression,
    AvatarPose,
    AvatarState,
    AvatarVisibility,
)

class Avatar:
    """Manage the current state of an avatar.

    The Avatar class contains state management only.
    It does not render anything and does not depend on a
    specific VTuber model or rendering technology.
    """

    def __init__(self, initial_state: AvatarState | None = None) -> None:
        self._state = initial_state or AvatarState()

    @property
    def state(self) -> AvatarState:
        """Return the current immutable Avatar state."""

        return self._state

    def apply(self, action: AvatarAction) -> AvatarState:
        """Apply an Avatar action and return the new state."""

        action_type = action.type

        if action_type is AvatarActionType.SET_ACTIVITY:
            self._state = self._state.with_activity(action.value)

        elif action_type is AvatarActionType.SET_EXPRESSION:
            self._state = self._state.with_expression(action.value)

        elif action_type is AvatarActionType.SET_POSE:
            self._state = self._state.with_pose(action.value)

        elif action_type is AvatarActionType.SET_VISIBILITY:
            self._state = self._state.with_visibility(action.value)

        elif action_type is AvatarActionType.SET_PARAMETER:
            self._state = self._state.with_parameter(action.parameter_name, float(action.value))

        elif action_type is AvatarActionType.RESET:
            self._state = AvatarState()

        else:
            raise ValueError(f"Unsupported Avatar action type: {action_type}.")

        return self._state

    def set_activity(self, activity: AvatarActivity) -> AvatarState:
        """Set the current high-level activity."""

        return self.apply(
            AvatarAction(type=AvatarActionType.SET_ACTIVITY, value=activity)
        )

    def set_expression(self, expression: AvatarExpression):        
        """Set the current expression."""

        return self.apply(
            AvatarAction(type=AvatarActionType.SET_EXPRESSION, value=expression)
        )

    def set_pose(self, pose: AvatarPose) -> AvatarState:
        """Set the current pose."""

        return self.apply(
            AvatarAction(type=AvatarActionType.SET_POSE, value=pose)
        )

    def set_visibility(self, visibility: AvatarVisibility) -> AvatarState:
        """Set the avatar visibility."""

        return self.apply(
            AvatarAction(type=AvatarActionType.SET_VISIBILITY, value=visibility)
        )

    def set_parameter(self, name: str, value: float) -> AvatarState:
        """Set one normalized Avatar parameter."""

        return self.apply(
            AvatarAction(
                type=AvatarActionType.SET_PARAMETER,
                parameter_name=name,
                value=value,
            )
        )

    def reset(self) -> AvatarState:
        """Reset the Avatar to its default state."""

        return self.apply(
            AvatarAction(type=AvatarActionType.RESET)
        )