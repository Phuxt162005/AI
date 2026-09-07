import json
import tempfile
import unittest
from pathlib import Path

from core.config import AppConfig
from core.exceptions import ConfigurationError


class TestAppConfig(unittest.TestCase):

    def test_default_config(self):
        config = AppConfig()

        self.assertEqual(config.name, "ProjectAI")
        self.assertEqual(config.version, "0.1.0")
        self.assertEqual(config.log_level, "INFO")
        self.assertEqual(config.model_dir, "models")
        self.assertEqual(config.data_dir, "data")

    def test_from_dict(self):
        config = AppConfig.from_dict({
            "name": "TestProject",
            "version": "1.0.0",
            "log_level": "DEBUG",
            "model_dir": "custom_models",
            "data_dir": "custom_data",
        })

        self.assertEqual(config.name, "TestProject")
        self.assertEqual(config.version, "1.0.0")
        self.assertEqual(config.log_level, "DEBUG")
        self.assertEqual(config.model_dir, "custom_models")
        self.assertEqual(config.data_dir, "custom_data")

    def test_load_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "config.json"

            path.write_text(
                json.dumps({
                    "name": "ProjectAI",
                    "version": "0.1.0",
                    "log_level": "INFO",
                    "model_dir": "models",
                    "data_dir": "data",
                }),
                encoding="utf-8",
            )

            config = AppConfig.load(path)

            self.assertEqual(config.name, "ProjectAI")
            self.assertEqual(config.version, "0.1.0")

    def test_missing_file(self):
        with self.assertRaises(ConfigurationError):
            AppConfig.load("missing_config.json")

    def test_invalid_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "invalid.json"
            path.write_text("{invalid}", encoding="utf-8")

            with self.assertRaises(ConfigurationError):
                AppConfig.load(path)


if __name__ == "__main__":
    unittest.main()