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
