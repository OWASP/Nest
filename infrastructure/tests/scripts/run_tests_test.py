"""Tests for ``scripts.run_tests`` CLI."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from scripts import run_tests
from scripts.errors import TestRunnerError


class TestRunTestsMain:
    """Tests for the ``run_tests`` CLI entrypoint."""

    @patch("scripts.run_tests.InfrastructureTestRunner")
    def test_main_unit(self, mock_runner_cls: MagicMock) -> None:
        mock_runner = mock_runner_cls.return_value
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = MagicMock(
                unit=True,
                integration=False,
                get_tag=False,
                get_image=False,
            )
            run_tests.main()
            mock_runner.configure_environment.assert_called_once()
            mock_runner.run_unit.assert_called_once()
            mock_runner.run_integration.assert_not_called()

    @patch("scripts.run_tests.InfrastructureTestRunner")
    def test_main_integration(self, mock_runner_cls: MagicMock) -> None:
        mock_runner = mock_runner_cls.return_value
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = MagicMock(
                unit=False,
                integration=True,
                get_tag=False,
                get_image=False,
            )
            run_tests.main()
            mock_runner.configure_environment.assert_called_once()
            mock_runner.run_integration.assert_called_once()
            mock_runner.run_unit.assert_not_called()

    @patch("scripts.run_tests.InfrastructureTestRunner")
    def test_main_get_tag(self, mock_runner_cls: MagicMock) -> None:
        mock_runner = mock_runner_cls.return_value
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = MagicMock(
                unit=False,
                integration=False,
                get_tag=True,
                get_image=False,
            )
            run_tests.main()
            mock_runner.configure_environment.assert_called_once()
            mock_runner.print_localstack_tag.assert_called_once()
            mock_runner.run_unit.assert_not_called()
            mock_runner.run_integration.assert_not_called()

    @patch("scripts.run_tests.InfrastructureTestRunner")
    def test_main_get_image(self, mock_runner_cls: MagicMock) -> None:
        mock_runner = mock_runner_cls.return_value
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = MagicMock(
                unit=False,
                integration=False,
                get_tag=False,
                get_image=True,
            )
            run_tests.main()
            mock_runner.configure_environment.assert_called_once()
            mock_runner.print_localstack_image.assert_called_once()
            mock_runner.run_unit.assert_not_called()
            mock_runner.run_integration.assert_not_called()

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
                get_image=False,
            )
            run_tests.main()
            mock_stderr_write.assert_any_call("Error: Mocked failure\n")
            mock_exit.assert_called_once_with(1)
