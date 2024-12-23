import unittest
from unittest.mock import patch, MagicMock
from main import DependencyVisualizer


class TestDependencyVisualizer(unittest.TestCase):
    def setUp(self):
        self.visualizer = DependencyVisualizer("config.json")

    @patch("subprocess.run")
    def test_get_dependencies(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Requires: urllib3, chardet, idna\n"
        )
        deps = self.visualizer.get_dependencies("requests")
        self.assertIn("requests", deps)
        self.assertIn("urllib3", deps["requests"])

    def test_generate_plantuml(self):
        dependencies = {"requests": {"urllib3", "chardet"}}
        plantuml_code = self.visualizer.generate_plantuml(dependencies)
        self.assertIn('"requests" -> "urllib3";', plantuml_code)
        self.assertIn('"requests" -> "chardet";', plantuml_code)


if __name__ == "__main__":
    unittest.main()