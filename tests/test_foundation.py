"""Tests for the temporary ProjectAI foundation components."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.types import InputData, InputType, OutputType
from self_built.foundation import (
    EchoModel,
    EchoTool,
    FoundationAgent,
    InMemoryMemory,
)

class TestEchoModel(unittest.TestCase):
    def test_model_must_be_loaded_before_prediction(self) -> None:
        model = EchoModel()
        with self.assertRaises(RuntimeError):
            model.predict("hello")

    def test_model_prediction(self) -> None:
        model = EchoModel()
        model.load()
        result = model.predict("hello")
        self.assertEqual(result, "hello")

    def test_model_metadata(self) -> None:
        model = EchoModel()
        metadata = model.metadata()
        self.assertEqual(metadata["name"], "EchoModel")

    def test_model_save(self) -> None:
        model = EchoModel()
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "model.txt"
            model.save(str(destination))
            self.assertTrue(destination.is_file())
            self.assertEqual(
                destination.read_text(encoding="utf-8"),
                "foundation-placeholder",
            )

class TestInMemoryMemory(unittest.TestCase):
    def test_store_and_retrieve(self) -> None:
        memory = InMemoryMemory()
        memory.store("name", "ProjectAI")
        self.assertEqual(memory.retrieve("name"), "ProjectAI")

    def test_update_existing_value(self) -> None:
        memory = InMemoryMemory()
        memory.store("name", "ProjectAI")
        memory.update("name", "ProjectAI Assistant")
        self.assertEqual(memory.retrieve("name"), "ProjectAI Assistant")

    def test_update_missing_key(self) -> None:
        memory = InMemoryMemory()
        with self.assertRaises(KeyError):
            memory.update("missing", "value")

    def test_delete_value(self) -> None:
        memory = InMemoryMemory()
        memory.store("name", "ProjectAI")
        memory.delete("name")
        self.assertIsNone(memory.retrieve("name"))

class TestEchoTool(unittest.TestCase):
    def test_tool_properties(self) -> None:
        tool = EchoTool()
        self.assertEqual(tool.name, "echo")
        self.assertTrue(tool.description)

    def test_tool_execution(self) -> None:
        tool = EchoTool()
        result = tool.execute({"value": "hello"})
        self.assertEqual(result, "hello")

class TestFoundationAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.model = EchoModel()
        self.model.load()
        self.memory = InMemoryMemory()
        self.tool = EchoTool()
        self.agent = FoundationAgent(
            model=self.model,
            memory=self.memory,
            tool=self.tool,
        )

    def test_agent_decision(self) -> None:
        decision = self.agent.decide({"input": "hello"})
        self.assertEqual(decision["action"], "model")

    def test_agent_process(self) -> None:
        input_data = InputData(type=InputType.TEXT, content="hello")
        output = self.agent.process(input_data)
        self.assertEqual(output.type, OutputType.TEXT)
        self.assertEqual(output.content, "hello")

    def test_agent_stores_last_input(self) -> None:
        input_data = InputData(type=InputType.TEXT, content="hello")
        self.agent.process(input_data)
        self.assertEqual(self.memory.retrieve("last_input"), "hello")

    def test_agent_model_communication(self) -> None:
        input_data = InputData(type=InputType.TEXT, content="ProjectAI")
        output = self.agent.process(input_data)
        self.assertEqual(output.content, "ProjectAI")

    def test_agent_tool_communication(self) -> None:
        class ToolAgent(FoundationAgent):
            def decide(
                self,
                context: dict[str, object],
            ) -> dict[str, str]:
                return {
                    "action": "tool",
                    "reason": "Test tool communication",
                }

        agent = ToolAgent(
            model=self.model,
            memory=self.memory,
            tool=self.tool,
        )
        input_data = InputData(
            type=InputType.TEXT,
            content="tool test",
        )
        output = agent.process(input_data)
        self.assertEqual(
            output.content,
            "tool test",
        )

if __name__ == "__main__":
    unittest.main()