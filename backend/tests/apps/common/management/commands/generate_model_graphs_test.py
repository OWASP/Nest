from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from django.core.management import CommandError
from django.test import SimpleTestCase

from apps.common.management.commands.generate_model_graphs import Command


class GenerateModelGraphsCommandTests(SimpleTestCase):
    def _app(self, name: str, label: str):
        app = MagicMock()
        app.name = name
        app.label = label
        return app

    @patch("apps.common.management.commands.generate_model_graphs.apps.get_app_configs")
    @patch("apps.common.management.commands.generate_model_graphs.call_command")
    def test_creates_output_directories_and_runs(self, mock_call, mock_apps):
        mock_apps.return_value = [
            self._app("apps.users", "users"),
            self._app("apps.projects", "projects"),
        ]

        with TemporaryDirectory() as tmpdir, self.settings(BASE_DIR=tmpdir):
            Command().handle()

            base_dir = Path("model-graphs")
            assert (base_dir / "apps").exists()
            assert (base_dir / "inter-app").exists()
            assert mock_call.called

    @patch("apps.common.management.commands.generate_model_graphs.apps.get_app_configs")
    @patch("apps.common.management.commands.generate_model_graphs.call_command")
    def test_only_project_apps_are_used(self, mock_call, mock_apps):
        mock_apps.return_value = [
            self._app("apps.users", "users"),
            self._app("django_rq", "django_rq"),
        ]

        Command().handle()

        called_labels = {
            call.args[1]
            for call in mock_call.call_args_list
            if call.args and call.args[0] == "graph_models"
        }

        assert "users" in called_labels
        assert "django_rq" not in called_labels

    @patch("apps.common.management.commands.generate_model_graphs.apps.get_app_configs")
    @patch("apps.common.management.commands.generate_model_graphs.call_command")
    def test_command_is_non_blocking_on_command_error(self, mock_call, mock_apps):
        mock_apps.return_value = [self._app("apps.users", "users")]

        error_msg = "inheritance graph failed"

        def side_effect(*args, **kwargs):
            _ = kwargs
            if "--inheritance" in args:
                raise CommandError(error_msg)

        mock_call.side_effect = side_effect

        Command().handle()

    @patch("apps.common.management.commands.generate_model_graphs.apps.get_app_configs")
    @patch("apps.common.management.commands.generate_model_graphs.call_command")
    def test_command_is_non_blocking_on_os_error(self, mock_call, mock_apps):
        mock_apps.return_value = [self._app("apps.users", "users")]

        error_msg = "dot binary missing"

        def side_effect(*args, **kwargs):
            _ = kwargs
            if "--no-inheritance" in args:
                raise OSError(error_msg)

        mock_call.side_effect = side_effect

        Command().handle()

    @patch("apps.common.management.commands.generate_model_graphs.apps.get_app_configs")
    @patch("apps.common.management.commands.generate_model_graphs.call_command")
    def test_no_apps_still_creates_directories(self, mock_call, mock_apps):
        mock_apps.return_value = []

        Command().handle()

        base_dir = Path("model-graphs")
        assert (base_dir / "apps").exists()
        assert (base_dir / "inter-app").exists()
