"""Tests for ``scripts.run_deploy`` CLI."""

from unittest.mock import MagicMock, patch

from scripts import run_deploy
from scripts.errors import TestRunnerError


class TestRunDeployMain:
    """Tests for the ``run_deploy`` CLI entrypoint."""

    @patch("scripts.run_deploy.InfrastructureDeployRunner")
    def test_main_invokes_configure_and_deploy(self, mock_runner_cls: MagicMock) -> None:
        mock_runner = mock_runner_cls.return_value

        with patch("argparse.ArgumentParser.parse_args"):
            run_deploy.main()

        mock_runner.configure_environment.assert_called_once()
        mock_runner.deploy.assert_called_once()

    @patch("scripts.run_deploy.InfrastructureDeployRunner")
    @patch("sys.exit")
    @patch("sys.stderr.write")
    def test_main_handles_test_runner_error(
        self,
        mock_stderr_write: MagicMock,
        mock_exit: MagicMock,
        mock_runner_cls: MagicMock,
    ) -> None:
        mock_runner = mock_runner_cls.return_value
        mock_runner.deploy.side_effect = TestRunnerError("boom")

        with patch("argparse.ArgumentParser.parse_args"):
            run_deploy.main()

        mock_stderr_write.assert_any_call("Error: boom\n")
        mock_exit.assert_called_once_with(1)
