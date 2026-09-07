from pathlib import Path
import tempfile
import unittest

from core.config import AppConfig
from core.exceptions import ConfigurationError


ROOT = Path(__file__).resolve().parents[1]


class ConfigurationTests(unittest.TestCase):
    def test_load_project_configuration(self):
        config = AppConfig.load(ROOT / "config.json")

        self.assertEqual(config.name, "ProjectAI")
        self.assertEqual(config.version, "0.1.0")
        self.assertEqual(config.log_level, "INFO")
        self.assertEqual(config.model_dir, "models")
        self.assertEqual(config.data_dir, "data")

    def test_missing_configuration(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.json"

            with self.assertRaises(ConfigurationError):
                AppConfig.load(path)

    def test_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.json"
            path.write_text("{invalid", encoding="utf-8")

            with self.assertRaises(ConfigurationError):
                AppConfig.load(path)

    def test_empty_name(self):
        with self.assertRaises(ConfigurationError):
            AppConfig.from_dict({
                "name": "",
                "version": "0.1.0",
            })

    def test_empty_version(self):
        with self.assertRaises(ConfigurationError):
            AppConfig.from_dict({
                "name": "ProjectAI",
                "version": "",
            })

    def test_invalid_log_level(self):
        with self.assertRaises(ConfigurationError):
            AppConfig.from_dict({
                "log_level": "INVALID",
            })

    def test_empty_model_dir(self):
        with self.assertRaises(ConfigurationError):
            AppConfig.from_dict({
                "model_dir": "",
            })

    def test_empty_data_dir(self):
        with self.assertRaises(ConfigurationError):
            AppConfig.from_dict({
                "data_dir": "",
            })


if __name__ == "__main__":
    unittest.main()