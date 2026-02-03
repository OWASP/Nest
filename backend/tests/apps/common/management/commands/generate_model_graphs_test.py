from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase


class GenerateModelGraphsCommandTests(SimpleTestCase):
    @patch("apps.common.management.commands.generate_model_graphs.call_command")
    def test_command_runs_successfully(self, mock_call_command):
        """
        Command runs successfully and creates output directories.
        """
        call_command("generate_model_graphs")

        base_dir = Path(settings.BASE_DIR) / "model-graphs"

        self.assertTrue(base_dir.exists())
        self.assertTrue((base_dir / "apps").exists())
        self.assertTrue((base_dir / "inter-app").exists())
        self.assertTrue(mock_call_command.called)

    @patch("apps.common.management.commands.generate_model_graphs.call_command")
    def test_command_is_non_blocking(self, mock_call_command):
        """
        Command remains non-blocking even if graph generation is skipped.
        """
        mock_call_command.return_value = None

        call_command("generate_model_graphs")

        self.assertTrue(mock_call_command.called)
