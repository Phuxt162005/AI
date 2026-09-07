"""Standard input/output data contracts shared by modules."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class InputType(str, Enum):
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"


class OutputType(str, Enum):
    TEXT = "text"
    VOICE = "voice"
    AVATAR = "avatar"


@dataclass
class InputData:
    type: InputType
    content: Any
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OutputData:
    type: OutputType
    content: Any
    metadata: dict[str, Any] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)