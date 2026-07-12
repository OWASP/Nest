"""Tests for ``scripts.run_tests`` CLI."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from scripts.errors import TestRunnerError


class TestRunTestsMain:
    """Tests for the ``run_tests`` CLI entrypoint."""

    @patch("scripts.commands.CommandRunner.require")
    @patch("sys.exit")
    @patch("sys.stderr.write")
    def test_main_handles_test_runner_error(
        self,
        mock_stderr_write: MagicMock,
        mock_exit: MagicMock,
        mock_require: MagicMock,
    ) -> None:
        mock_require.side_effect = TestRunnerError("Mocked failure")
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = MagicMock(
                unit=True,
                integration=False,
                get_tag=False,
            )
            from scripts import run_tests

            run_tests.main()
            mock_stderr_write.assert_any_call("Error: Mocked failure\n")
            mock_exit.assert_called_once_with(1)
