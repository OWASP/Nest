"""Tests for ``scripts.run_backend_task`` CLI."""

from unittest.mock import MagicMock, patch

from scripts import run_backend_task
from scripts.errors import RunnerError


class TestRunBackendTaskMain:
    """Tests for the ``run_backend_task`` CLI entrypoint."""

    @patch("sys.argv", ["run_backend_task", "migrate"])
    @patch("scripts.run_backend_task.BackendTaskRunner")
    def test_main_runs_selected_task(self, mock_runner_cls: MagicMock) -> None:
        mock_runner = mock_runner_cls.return_value

        run_backend_task.main()

        mock_runner_cls.assert_called_once_with("migrate")
        mock_runner.run.assert_called_once_with()

    @patch("sys.argv", ["run_backend_task", "migrate"])
    @patch("scripts.run_backend_task.BackendTaskRunner")
    @patch("sys.exit")
    @patch("sys.stderr.write")
    def test_main_handles_runner_error(
        self,
        mock_stderr_write: MagicMock,
        mock_exit: MagicMock,
        mock_runner_cls: MagicMock,
    ) -> None:
        mock_runner = mock_runner_cls.return_value
        mock_runner.run.side_effect = RunnerError("boom")

        run_backend_task.main()

        mock_stderr_write.assert_any_call("Error: boom\n")
        mock_exit.assert_called_once_with(1)
