from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings


class GenerateModelGraphsCommandTests(SimpleTestCase):
    @patch("apps.common.management.commands.generate_model_graphs.call_command")
    def test_command_runs_successfully(self, mock_call_command):
        """Command runs successfully and creates output directories."""
        with TemporaryDirectory() as tmpdir, override_settings(BASE_DIR=tmpdir):
            call_command("generate_model_graphs")

            base_dir = Path(settings.BASE_DIR) / "model-graphs"

            assert base_dir.exists()
            assert (base_dir / "apps").exists()
            assert (base_dir / "inter-app").exists()
            mock_call_command.assert_called()

    @patch("apps.common.management.commands.generate_model_graphs.call_command")
    def test_command_is_non_blocking(self, mock_call_command):
        """Command remains non-blocking when graph generation is skipped."""
        with TemporaryDirectory() as tmpdir, override_settings(BASE_DIR=tmpdir):
            mock_call_command.return_value = None

            call_command("generate_model_graphs")

            mock_call_command.assert_called()
