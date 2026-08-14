"""Tests for ``scripts.deploy_runner``."""

import logging
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.deploy_runner import InfrastructureDeployRunner


class TestInfrastructureDeployRunner:
    """Tests for ``InfrastructureDeployRunner`` orchestration."""

    @patch.dict(os.environ, {}, clear=True)
    @patch("pathlib.Path.mkdir")
    def test_configure_environment(self, mock_mkdir: MagicMock) -> None:
        runner = InfrastructureDeployRunner(root_dir=Path("/repo"))

        with patch("os.chdir") as mock_chdir:
            runner.configure_environment()

            mock_chdir.assert_called_once_with(Path("/repo"))
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

            expected_dir = str(Path.home() / ".terraform.d" / "plugin-cache")
            assert os.environ["TF_PLUGIN_CACHE_DIR"] == expected_dir

    @patch.dict(os.environ, {}, clear=True)
    @patch("pathlib.Path.mkdir", side_effect=OSError("nope"))
    def test_configure_environment_swallows_cache_failure(
        self,
        mock_mkdir: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        runner = InfrastructureDeployRunner(root_dir=Path("/repo"))

        with patch("os.chdir"), caplog.at_level(logging.WARNING):
            runner.configure_environment()

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        assert "TF_PLUGIN_CACHE_DIR" not in os.environ
        assert "Could not configure TF_PLUGIN_CACHE_DIR" in caplog.text
