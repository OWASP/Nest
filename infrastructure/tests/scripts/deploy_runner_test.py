"""Tests for ``scripts.deploy_runner``."""

import logging
import os
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from scripts.commands import CommandRunner
from scripts.deploy_runner import InfrastructureDeployRunner
from scripts.errors import RunnerError
from scripts.localstack import LocalStack

LOCALSTACK_ENDPOINT_URL = "http://localstack:4566"  # NOSONAR: Test-only LocalStack HTTP.


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

    @patch.dict(os.environ, {}, clear=True)
    def test_deploy_runs_init_and_apply(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.api_url = LOCALSTACK_ENDPOINT_URL

        captured: dict[str, str] = {}

        def capture(*_args: object, **_kwargs: object) -> MagicMock:
            captured.setdefault("AWS_ACCESS_KEY_ID", os.environ["AWS_ACCESS_KEY_ID"])
            captured.setdefault("AWS_ENDPOINT_URL", os.environ["AWS_ENDPOINT_URL"])
            captured.setdefault("AWS_SECRET_ACCESS_KEY", os.environ["AWS_SECRET_ACCESS_KEY"])
            return MagicMock(returncode=0)

        commands.run.side_effect = capture

        runner = InfrastructureDeployRunner(
            root_dir=Path("/repo"),
            commands=commands,
            localstack=localstack,
        )

        runner.deploy()

        commands.require.assert_called_once_with("tflocal")
        localstack.wait_ready.assert_called_once()

        live_dir = str(Path("/repo") / "infrastructure" / "live")
        commands.run.assert_has_calls(
            [
                call(
                    "tflocal",
                    f"-chdir={live_dir}",
                    "init",
                    "-backend-config=terraform.localstack.tfbackend",
                    "-input=false",
                    "-reconfigure",
                    check=False,
                ),
                call(
                    "tflocal",
                    f"-chdir={live_dir}",
                    "apply",
                    "-auto-approve",
                    "-input=false",
                    "-var-file=terraform.localstack.tfvars",
                    check=False,
                ),
            ]
        )
        fake_credential = "test"
        assert captured["AWS_ACCESS_KEY_ID"] == fake_credential
        assert captured["AWS_SECRET_ACCESS_KEY"] == fake_credential
        assert captured["AWS_ENDPOINT_URL"] == LOCALSTACK_ENDPOINT_URL
        assert "AWS_ACCESS_KEY_ID" not in os.environ
        assert "AWS_SECRET_ACCESS_KEY" not in os.environ
        assert "AWS_ENDPOINT_URL" not in os.environ

    def test_deploy_propagates_wait_ready_failure(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.wait_ready.side_effect = RunnerError("localstack down")

        runner = InfrastructureDeployRunner(
            root_dir=Path("/repo"),
            commands=commands,
            localstack=localstack,
        )

        with pytest.raises(RunnerError, match="localstack down"):
            runner.deploy()

        commands.run.assert_not_called()

    @patch.dict(os.environ, {}, clear=True)
    def test_deploy_raises_runner_error_when_init_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=1)
        localstack = MagicMock(spec=LocalStack)
        localstack.api_url = LOCALSTACK_ENDPOINT_URL

        runner = InfrastructureDeployRunner(
            root_dir=Path("/repo"),
            commands=commands,
            localstack=localstack,
        )

        with pytest.raises(RunnerError, match="terraform init failed"):
            runner.deploy()

        assert commands.run.call_count == 1
        assert "AWS_ACCESS_KEY_ID" not in os.environ
        assert "AWS_SECRET_ACCESS_KEY" not in os.environ
        assert "AWS_ENDPOINT_URL" not in os.environ

    @patch.dict(os.environ, {}, clear=True)
    def test_deploy_raises_runner_error_when_apply_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [MagicMock(returncode=0), MagicMock(returncode=1)]
        localstack = MagicMock(spec=LocalStack)
        localstack.api_url = LOCALSTACK_ENDPOINT_URL

        runner = InfrastructureDeployRunner(
            root_dir=Path("/repo"),
            commands=commands,
            localstack=localstack,
        )

        with pytest.raises(RunnerError, match="terraform apply failed"):
            runner.deploy()

        assert commands.run.call_count == 2
        assert "AWS_ACCESS_KEY_ID" not in os.environ
        assert "AWS_SECRET_ACCESS_KEY" not in os.environ
        assert "AWS_ENDPOINT_URL" not in os.environ
