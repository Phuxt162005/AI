"""System integration layer for ProjectAI."""

from __future__ import annotations

from core.types import InputData, OutputData
from self_built.agent import ProjectAgent


class SystemIntegration:
    """Connect the application input/output with ProjectAI Agent."""

    def __init__(self, agent: ProjectAgent) -> None:
        if not isinstance(agent, ProjectAgent):
            raise TypeError("agent must be a ProjectAgent.")

        self._agent = agent

    @property
    def agent(self) -> ProjectAgent:
        """Return the configured ProjectAI Agent."""

        return self._agent

    def process(self, input_data: InputData) -> OutputData:
        """Process one user input through the integrated system."""

        if not isinstance(input_data, InputData):
            raise TypeError("input_data must be an InputData.")

        return self._agent.process(input_data)