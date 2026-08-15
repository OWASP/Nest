"""Tests for ``scripts.tests_runner``."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.commands import CommandRunner
from scripts.localstack import LOCALSTACK_PORT, LocalStack, OverrideManager
from scripts.terraform_tests import ExecutionMode, TerraformTests
from scripts.tests_runner import InfrastructureTestRunner

EXTERNAL_LOCALSTACK_ENDPOINT_URL = (
    f"http://localstack:{LOCALSTACK_PORT}"  # NOSONAR: Test-only LocalStack HTTP.
)
LOCALSTACK_ENDPOINT_URL = (
    f"http://localhost:{LOCALSTACK_PORT}"  # NOSONAR: Test-only LocalStack HTTP.
)
PRIOR_ACCESS_KEY_ID = "prior-access-key"


def assert_aws_credentials_set(captured: dict[str, str], expected_endpoint: str) -> None:
    """Assert AWS creds were set to LocalStack test values during the run and unset after."""
    fake_credential = "test"
    assert captured["AWS_ACCESS_KEY_ID"] == fake_credential
    assert captured["AWS_SECRET_ACCESS_KEY"] == fake_credential
    assert captured["AWS_ENDPOINT_URL"] == expected_endpoint
    assert "AWS_ACCESS_KEY_ID" not in os.environ
    assert "AWS_SECRET_ACCESS_KEY" not in os.environ
    assert "AWS_ENDPOINT_URL" not in os.environ


def capture_aws_env_vars(terraform_tests: MagicMock) -> dict[str, str]:
    """Capture AWS env vars while discovery runs."""
    captured: dict[str, str] = {}

    def capture(*_args: object, **_kwargs: object) -> None:
        captured["AWS_ACCESS_KEY_ID"] = os.environ["AWS_ACCESS_KEY_ID"]
        captured["AWS_ENDPOINT_URL"] = os.environ["AWS_ENDPOINT_URL"]
        captured["AWS_SECRET_ACCESS_KEY"] = os.environ["AWS_SECRET_ACCESS_KEY"]

    terraform_tests.discover_and_run.side_effect = capture
    return captured


def integration_runner(
    *,
    healthy: bool = True,
    can_start_container: bool = True,
    host: str = "localhost",
    api_url: str = LOCALSTACK_ENDPOINT_URL,
    image: tuple[str, str] = ("localstack/localstack:1.0", "1.0"),
    root_dir: Path = Path("/repo"),
    cleanup_error: BaseException | None = None,
) -> tuple[
    InfrastructureTestRunner,
    MagicMock,
    MagicMock,
    MagicMock,
    MagicMock,
    dict[str, str],
]:
    """Build a runner with mocked integration dependencies."""
    commands = MagicMock(spec=CommandRunner)
    localstack = MagicMock(spec=LocalStack)
    localstack.port = LOCALSTACK_PORT
    localstack.host = host
    localstack.api_url = api_url
    localstack.can_start_container = can_start_container
    localstack.healthy.return_value = healthy
    localstack.image_info.return_value = image
    overrides = MagicMock(spec=OverrideManager)
    if cleanup_error is not None:
        overrides.cleanup.side_effect = cleanup_error
    terraform_tests = MagicMock(spec=TerraformTests)
    captured = capture_aws_env_vars(terraform_tests)

    runner = InfrastructureTestRunner(
        root_dir=root_dir,
        commands=commands,
        localstack=localstack,
        overrides=overrides,
        terraform_tests=terraform_tests,
    )
    return runner, commands, localstack, overrides, terraform_tests, captured


class TestInfrastructureTestRunner:
    """Tests for ``InfrastructureTestRunner`` orchestration."""

    @patch.dict(os.environ, {}, clear=True)
    @patch("pathlib.Path.mkdir")
    def test_configure_environment(self, mock_mkdir: MagicMock) -> None:
        runner = InfrastructureTestRunner(root_dir=Path("/repo"))

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
        runner = InfrastructureTestRunner(root_dir=Path("/repo"))

        with patch("os.chdir"), caplog.at_level(logging.WARNING):
            runner.configure_environment()

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        assert "TF_PLUGIN_CACHE_DIR" not in os.environ
        assert "Could not configure TF_PLUGIN_CACHE_DIR" in caplog.text

    @patch("sys.stdout.write")
    def test_print_localstack_tag(self, mock_write: MagicMock) -> None:
        localstack = MagicMock(spec=LocalStack)
        localstack.image_info.return_value = ("localstack/localstack:1.0", "1.0")
        runner = InfrastructureTestRunner(root_dir=Path("/repo"), localstack=localstack)

        runner.print_localstack_tag()

        localstack.image_info.assert_called_once_with(Path("/repo"))
        mock_write.assert_called_once_with("1.0\n")

    @patch("sys.stdout.write")
    def test_print_localstack_image(self, mock_write: MagicMock) -> None:
        localstack = MagicMock(spec=LocalStack)
        localstack.image_info.return_value = ("localstack/localstack:1.0", "1.0")
        runner = InfrastructureTestRunner(root_dir=Path("/repo"), localstack=localstack)

        runner.print_localstack_image()

        localstack.image_info.assert_called_once_with(Path("/repo"))
        mock_write.assert_called_once_with("localstack/localstack:1.0\n")

    def test_run_unit(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        terraform_tests = MagicMock(spec=TerraformTests)
        runner = InfrastructureTestRunner(
            root_dir=Path("/repo"),
            commands=commands,
            terraform_tests=terraform_tests,
        )

        runner.run_unit()

        commands.require.assert_called_once_with("tflocal")
        terraform_tests.discover_and_run.assert_called_once_with(ExecutionMode.UNIT)

    @patch.dict(os.environ, {}, clear=True)
    def test_run_integration_uses_existing_localstack(self) -> None:
        runner, _, localstack, overrides, terraform_tests, captured = integration_runner()

        runner.run_integration()

        localstack.start.assert_not_called()
        localstack.wait_ready.assert_called_once()
        overrides.write.assert_called_once()
        terraform_tests.discover_and_run.assert_called_once_with(ExecutionMode.INTEGRATION)
        overrides.cleanup.assert_called_once()
        localstack.stop.assert_not_called()
        assert_aws_credentials_set(captured, LOCALSTACK_ENDPOINT_URL)

    @patch.dict(os.environ, {}, clear=True)
    def test_run_integration_starts_localstack_when_docker_available(self) -> None:
        runner, _, localstack, _, terraform_tests, captured = integration_runner(healthy=False)

        runner.run_integration()

        localstack.start.assert_called_once_with("localstack/localstack:1.0")
        localstack.wait_ready.assert_called_once()
        localstack.stop.assert_called_once()
        terraform_tests.discover_and_run.assert_called_once_with(ExecutionMode.INTEGRATION)
        assert_aws_credentials_set(captured, LOCALSTACK_ENDPOINT_URL)

    @patch.dict(os.environ, {}, clear=True)
    def test_run_integration_stops_localstack_when_cleanup_fails(self) -> None:
        runner, _, localstack, overrides, _, captured = integration_runner(
            healthy=False,
            image=("localstack/localstack:1.0-alt", "1.0"),
            root_dir=Path("/repo-alt"),
            cleanup_error=RuntimeError("cleanup failed"),
        )

        with pytest.raises(RuntimeError, match="cleanup failed"):
            runner.run_integration()

        overrides.cleanup.assert_called_once()
        localstack.stop.assert_called_once()
        assert_aws_credentials_set(captured, LOCALSTACK_ENDPOINT_URL)

    @patch.dict(os.environ, {}, clear=True)
    def test_run_integration_waits_for_external_localstack(self) -> None:
        runner, commands, localstack, _, terraform_tests, captured = integration_runner(
            healthy=False,
            can_start_container=False,
            host="localstack",
            api_url=EXTERNAL_LOCALSTACK_ENDPOINT_URL,
            root_dir=Path("/repo-alt"),
        )

        runner.run_integration()

        commands.require.assert_called_once_with("tflocal")
        localstack.start.assert_not_called()
        localstack.wait_ready.assert_called_once()
        localstack.stop.assert_not_called()
        terraform_tests.discover_and_run.assert_called_once_with(ExecutionMode.INTEGRATION)
        assert_aws_credentials_set(captured, EXTERNAL_LOCALSTACK_ENDPOINT_URL)

    @patch.dict(os.environ, {"AWS_ACCESS_KEY_ID": PRIOR_ACCESS_KEY_ID}, clear=True)
    def test_run_integration_restores_previous_credentials(self) -> None:
        runner, _, _, _, _, captured = integration_runner()

        runner.run_integration()

        assert captured["AWS_ACCESS_KEY_ID"] == "test"
        assert os.environ["AWS_ACCESS_KEY_ID"] == PRIOR_ACCESS_KEY_ID
