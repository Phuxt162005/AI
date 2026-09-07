import unittest

from core.interfaces import (
    AgentInterface,
    MemoryInterface,
    ModelInterface,
    ToolInterface,
)
from core.types import InputData, InputType, OutputData, OutputType


class TestModelInterface(unittest.TestCase):

    def test_model_interface_is_abstract(self):
        with self.assertRaises(TypeError):
            ModelInterface()


class TestMemoryInterface(unittest.TestCase):

    def test_memory_interface_is_abstract(self):
        with self.assertRaises(TypeError):
            MemoryInterface()


class TestToolInterface(unittest.TestCase):

    def test_tool_interface_is_abstract(self):
        with self.assertRaises(TypeError):
            ToolInterface()


class TestAgentInterface(unittest.TestCase):

    def test_agent_interface_is_abstract(self):
        with self.assertRaises(TypeError):
            AgentInterface()


class TestIOContracts(unittest.TestCase):

    def test_input_data(self):
        data = InputData(
            type=InputType.TEXT,
            content="Hello ProjectAI",
        )

        self.assertEqual(data.type, InputType.TEXT)
        self.assertEqual(data.content, "Hello ProjectAI")
        self.assertEqual(data.metadata, {})

    def test_output_data(self):
        data = OutputData(
            type=OutputType.TEXT,
            content="Hello!",
        )

        self.assertEqual(data.type, OutputType.TEXT)
        self.assertEqual(data.content, "Hello!")
        self.assertEqual(data.metadata, {})
        self.assertEqual(data.state, {})


if __name__ == "__main__":
    unittest.main()