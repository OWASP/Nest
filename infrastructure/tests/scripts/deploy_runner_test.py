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
AWS_ENV_VARS = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_ENDPOINT_URL")
FAKE_CREDENTIAL = "test"


def assert_aws_env_unset() -> None:
    for var in AWS_ENV_VARS:
        assert var not in os.environ


def build_runner(commands: MagicMock, localstack: MagicMock) -> InfrastructureDeployRunner:
    return InfrastructureDeployRunner(
        root_dir=Path("/repo"),
        commands=commands,
        localstack=localstack,
    )


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

    def test_apply_state_runs_init_and_apply(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=0)
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        runner.apply_state()

        state_dir = str(Path("/repo") / "infrastructure" / "state")
        commands.run.assert_has_calls(
            [
                call(
                    "tflocal",
                    f"-chdir={state_dir}",
                    "init",
                    "-input=false",
                    "-reconfigure",
                    check=False,
                ),
                call(
                    "tflocal",
                    f"-chdir={state_dir}",
                    "apply",
                    "-auto-approve",
                    "-input=false",
                    "-var-file=terraform.localstack.tfvars",
                    check=False,
                ),
            ]
        )

    def test_apply_state_raises_when_init_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=1)
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        with pytest.raises(RunnerError, match="terraform init failed"):
            runner.apply_state()

    def test_apply_state_raises_when_apply_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [MagicMock(returncode=0), MagicMock(returncode=1)]
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        with pytest.raises(RunnerError, match="terraform apply failed"):
            runner.apply_state()

    def test_apply_live_runs_init_and_apply(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=0)
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        runner.apply_live()

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

    def test_apply_live_raises_when_init_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=1)
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        with pytest.raises(RunnerError, match="terraform init failed"):
            runner.apply_live()

    def test_apply_live_raises_when_apply_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [MagicMock(returncode=0), MagicMock(returncode=1)]
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        with pytest.raises(RunnerError, match="terraform apply failed"):
            runner.apply_live()

    @patch.dict(os.environ, {}, clear=True)
    def test_deploy_calls_apply_state_then_apply_live_inside_aws_env(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.api_url = LOCALSTACK_ENDPOINT_URL
        runner = build_runner(commands, localstack)

        call_order: list[str] = []
        captured: dict[str, str] = {}

        def record_state() -> None:
            call_order.append("apply_state")
            for var in AWS_ENV_VARS:
                captured[var] = os.environ[var]

        def record_live() -> None:
            call_order.append("apply_live")

        with (
            patch.object(runner, "apply_state", side_effect=record_state) as mock_state,
            patch.object(runner, "apply_live", side_effect=record_live) as mock_live,
        ):
            runner.deploy()

        commands.require.assert_called_once_with("tflocal")
        localstack.wait_ready.assert_called_once()
        mock_state.assert_called_once_with()
        mock_live.assert_called_once_with()
        assert call_order == ["apply_state", "apply_live"]
        assert captured["AWS_ACCESS_KEY_ID"] == FAKE_CREDENTIAL
        assert captured["AWS_SECRET_ACCESS_KEY"] == FAKE_CREDENTIAL
        assert captured["AWS_ENDPOINT_URL"] == LOCALSTACK_ENDPOINT_URL
        assert_aws_env_unset()

    def test_deploy_propagates_wait_ready_failure(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.wait_ready.side_effect = RunnerError("localstack down")
        runner = build_runner(commands, localstack)

        with pytest.raises(RunnerError, match="localstack down"):
            runner.deploy()

        commands.run.assert_not_called()

    @patch.dict(os.environ, {}, clear=True)
    def test_refresh_calls_apply_live_inside_aws_env(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.api_url = LOCALSTACK_ENDPOINT_URL
        runner = build_runner(commands, localstack)

        captured: dict[str, str] = {}

        def record_live() -> None:
            for var in AWS_ENV_VARS:
                captured[var] = os.environ[var]

        with patch.object(runner, "apply_live", side_effect=record_live) as mock_live:
            runner.refresh()

        commands.require.assert_called_once_with("tflocal")
        localstack.wait_ready.assert_called_once()
        mock_live.assert_called_once_with()
        assert captured["AWS_ACCESS_KEY_ID"] == FAKE_CREDENTIAL
        assert captured["AWS_SECRET_ACCESS_KEY"] == FAKE_CREDENTIAL
        assert captured["AWS_ENDPOINT_URL"] == LOCALSTACK_ENDPOINT_URL
        assert_aws_env_unset()

    def test_refresh_propagates_wait_ready_failure(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.wait_ready.side_effect = RunnerError("localstack down")
        runner = build_runner(commands, localstack)

        with pytest.raises(RunnerError, match="localstack down"):
            runner.refresh()

        commands.run.assert_not_called()
