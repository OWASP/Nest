"""Tests for ``scripts.run_sync_params`` CLI."""

from unittest.mock import MagicMock, patch

from scripts import run_sync_params
from scripts.errors import RunnerError


class TestRunSyncParamsMain:
    """Tests for the ``run_sync_params`` CLI entrypoint."""

    @patch("sys.argv", ["run_sync_params"])
    @patch("scripts.run_sync_params.InfrastructureParameterSyncRunner")
    def test_main_defaults_to_production_configuration(
        self,
        mock_runner_cls: MagicMock,
    ) -> None:
        mock_runner = mock_runner_cls.return_value

        run_sync_params.main()

        mock_runner.sync.assert_called_once_with(
            configuration="Production",
            settings_module="settings.production",
        )

    @patch(
        "sys.argv",
        [
            "run_sync_params",
            "--configuration",
            "Local",
            "--settings-module",
            "settings.local",
        ],
    )
    @patch("scripts.run_sync_params.InfrastructureParameterSyncRunner")
    def test_main_passes_overrides(self, mock_runner_cls: MagicMock) -> None:
        mock_runner = mock_runner_cls.return_value

        run_sync_params.main()

        mock_runner.sync.assert_called_once_with(
            configuration="Local",
            settings_module="settings.local",
        )

    @patch("sys.argv", ["run_sync_params"])
    @patch("scripts.run_sync_params.InfrastructureParameterSyncRunner")
    @patch("sys.exit")
    @patch("sys.stderr.write")
    def test_main_handles_runner_error(
        self,
        mock_stderr_write: MagicMock,
        mock_exit: MagicMock,
        mock_runner_cls: MagicMock,
    ) -> None:
        mock_runner = mock_runner_cls.return_value
        mock_runner.sync.side_effect = RunnerError("boom")

        run_sync_params.main()

        mock_stderr_write.assert_any_call("Error: boom\n")
        mock_exit.assert_called_once_with(1)
