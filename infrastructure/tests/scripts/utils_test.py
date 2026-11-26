"""Tests for ``scripts.utils``."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.errors import RunnerError
from scripts.utils import (
    chdir_repository_root,
    configure_terraform_cache,
    init_live_configuration,
    localstack_aws_env,
    read_live_output,
    set_temporary_env,
)

FAKE_CREDENTIAL = "test"
TMP_VAR = "NEST_TEMPORARY_ENV_TEST"


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
            chdir_repository_root(Path("/repo"))
            mock_chdir.assert_called_once_with(Path("/repo"))


class TestInitLiveConfiguration:
    """Tests for ``init_live_configuration``."""

    def test_runs_terraform_init(self) -> None:
        commands = MagicMock()
        commands.run.return_value = MagicMock(returncode=0)

        init_live_configuration(commands, Path("/repo/live"), "terraform.tfbackend")

        commands.run.assert_called_once_with(
            "tflocal",
            "-chdir=/repo/live",
            "init",
            "-backend-config=terraform.tfbackend",
            "-input=false",
            "-reconfigure",
            check=False,
        )

    def test_raises_when_init_fails(self) -> None:
        commands = MagicMock()
        commands.run.return_value = MagicMock(returncode=1)

        with pytest.raises(RunnerError, match="terraform init failed"):
            init_live_configuration(commands, Path("/repo/live"), "terraform.tfbackend")


class TestLocalStackAwsEnv:
    """Tests for ``localstack_aws_env``."""

    @pytest.fixture(autouse=True)
    def _clean_env(self) -> None:
        for var in ("AWS_ACCESS_KEY_ID", "AWS_ENDPOINT_URL", "AWS_SECRET_ACCESS_KEY"):
            os.environ.pop(var, None)

    @patch.dict(os.environ, {}, clear=True)
    def test_sets_and_restores_aws_environment(self) -> None:
        with localstack_aws_env("http://localhost:4566"):  # NOSONAR
            assert os.environ["AWS_ACCESS_KEY_ID"] == FAKE_CREDENTIAL
            assert os.environ["AWS_ENDPOINT_URL"] == "http://localhost:4566"
            assert os.environ["AWS_SECRET_ACCESS_KEY"] == FAKE_CREDENTIAL

        for var in ("AWS_ACCESS_KEY_ID", "AWS_ENDPOINT_URL", "AWS_SECRET_ACCESS_KEY"):
            assert var not in os.environ

    def test_restores_previous_values(self) -> None:
        os.environ["AWS_ACCESS_KEY_ID"] = "original"
        with localstack_aws_env("http://localhost:4566"):  # NOSONAR
            assert os.environ["AWS_ACCESS_KEY_ID"] == FAKE_CREDENTIAL
        assert os.environ["AWS_ACCESS_KEY_ID"] == "original"


class TestReadLiveOutput:
    """Tests for ``read_live_output``."""

    def test_returns_stripped_raw_value(self) -> None:
        commands = MagicMock()
        commands.run.return_value = MagicMock(returncode=0, stdout="value\n")

        assert read_live_output(commands, Path("/repo/live"), "name") == "value"

        commands.run.assert_called_once_with(
            "tflocal",
            "-chdir=/repo/live",
            "output",
            "-raw",
            "name",
            capture_output=True,
            check=False,
        )

    def test_returns_parsed_json_value(self) -> None:
        commands = MagicMock()
        commands.run.return_value = MagicMock(returncode=0, stdout='["subnet-1"]\n')

        value = read_live_output(commands, Path("/repo/live"), "name", json_output=True)

        assert value == ["subnet-1"]
        commands.run.assert_called_once_with(
            "tflocal",
            "-chdir=/repo/live",
            "output",
            "-json",
            "name",
            capture_output=True,
            check=False,
        )

    def test_raises_when_output_fails(self) -> None:
        commands = MagicMock()
        commands.run.return_value = MagicMock(returncode=1, stderr="no state")

        with pytest.raises(RunnerError, match="terraform output failed"):
            read_live_output(commands, Path("/repo/live"), "name")


class TestTemporaryEnv:
    """Tests for ``temporary_env``."""

    @pytest.fixture(autouse=True)
    def _clean_env(self) -> None:
        os.environ.pop(TMP_VAR, None)

    def test_sets_and_unsets_when_previously_absent(self) -> None:
        with set_temporary_env(TMP_VAR, "value"):
            assert os.environ[TMP_VAR] == "value"
        assert TMP_VAR not in os.environ

    def test_restores_previous_value(self) -> None:
        os.environ[TMP_VAR] = "original"
        with set_temporary_env(TMP_VAR, "override"):
            assert os.environ[TMP_VAR] == "override"
        assert os.environ[TMP_VAR] == "original"

    def test_restores_on_exception(self) -> None:
        os.environ[TMP_VAR] = "original"
        with pytest.raises(RuntimeError), set_temporary_env(TMP_VAR, "override"):
            raise RuntimeError
        assert os.environ[TMP_VAR] == "original"

    def test_unsets_on_exception_when_previously_absent(self) -> None:
        with pytest.raises(RuntimeError), set_temporary_env(TMP_VAR, "value"):
            raise RuntimeError
        assert TMP_VAR not in os.environ
