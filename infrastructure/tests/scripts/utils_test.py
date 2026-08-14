"""Tests for ``scripts.utils``."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.utils import configure_terraform_cache, enter_repo_root, temporary_env

VAR = "NEST_TEMPORARY_ENV_TEST"


class TestConfigureTerraformCache:
    """Tests for ``configure_terraform_cache``."""

    @patch.dict(os.environ, {}, clear=True)
    @patch("pathlib.Path.mkdir")
    def test_creates_cache_and_exports_env(self, mock_mkdir: MagicMock) -> None:
        configure_terraform_cache()

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        expected = str(Path.home() / ".terraform.d" / "plugin-cache")
        assert os.environ["TF_PLUGIN_CACHE_DIR"] == expected

    @patch.dict(os.environ, {}, clear=True)
    @patch("pathlib.Path.mkdir", side_effect=OSError("nope"))
    def test_propagates_mkdir_failure(self, mock_mkdir: MagicMock) -> None:
        with pytest.raises(OSError, match="nope"):
            configure_terraform_cache()

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        assert "TF_PLUGIN_CACHE_DIR" not in os.environ


class TestEnterRepoRoot:
    """Tests for ``enter_repo_root``."""

    def test_changes_directory(self) -> None:
        with patch("os.chdir") as mock_chdir:
            enter_repo_root(Path("/repo"))
            mock_chdir.assert_called_once_with(Path("/repo"))


class TestTemporaryEnv:
    """Tests for ``temporary_env``."""

    @pytest.fixture(autouse=True)
    def _clean_env(self) -> None:
        os.environ.pop(VAR, None)

    def test_sets_and_unsets_when_previously_absent(self) -> None:
        with temporary_env(VAR, "value"):
            assert os.environ[VAR] == "value"
        assert VAR not in os.environ

    def test_restores_previous_value(self) -> None:
        os.environ[VAR] = "original"
        with temporary_env(VAR, "override"):
            assert os.environ[VAR] == "override"
        assert os.environ[VAR] == "original"

    def test_restores_on_exception(self) -> None:
        os.environ[VAR] = "original"
        with pytest.raises(RuntimeError), temporary_env(VAR, "override"):
            raise RuntimeError
        assert os.environ[VAR] == "original"

    def test_unsets_on_exception_when_previously_absent(self) -> None:
        with pytest.raises(RuntimeError), temporary_env(VAR, "value"):
            raise RuntimeError
        assert VAR not in os.environ
