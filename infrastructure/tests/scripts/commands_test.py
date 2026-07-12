"""Tests for ``scripts.commands``."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from scripts.commands import CommandRunner
from scripts.errors import CommandNotFoundError


class TestCommandRunner:
    """Tests for ``CommandRunner``."""

    @patch("shutil.which")
    def test_require_exists(self, mock_which: MagicMock) -> None:
        mock_which.return_value = "/usr/bin/terraform"
        assert CommandRunner().require("terraform") == "/usr/bin/terraform"

    @patch("shutil.which")
    def test_require_missing(self, mock_which: MagicMock) -> None:
        mock_which.return_value = None
        with pytest.raises(CommandNotFoundError):
            CommandRunner().require("nonexistent-cmd")

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_run_resolves_executable_and_args(
        self,
        mock_which: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        mock_which.return_value = "/usr/bin/terraform"
        completed = MagicMock()
        mock_run.return_value = completed

        result = CommandRunner().run("terraform", "init", "-backend=false")

        assert result is completed
        mock_run.assert_called_once_with(
            ["/usr/bin/terraform", "init", "-backend=false"],
            check=False,
            capture_output=False,
            text=True,
        )

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_run_forwards_check_and_capture_output(
        self,
        mock_which: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        mock_which.return_value = "/usr/bin/docker"
        CommandRunner().run("docker", "info", check=True, capture_output=True)
        mock_run.assert_called_once_with(
            ["/usr/bin/docker", "info"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_run_missing_command(self, mock_which: MagicMock, mock_run: MagicMock) -> None:
        mock_which.return_value = None
        runner = CommandRunner()
        with pytest.raises(CommandNotFoundError):
            runner.run("missing")
        mock_run.assert_not_called()
