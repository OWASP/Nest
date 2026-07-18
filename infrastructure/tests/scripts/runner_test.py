"""Tests for ``scripts.runner``."""

from __future__ import annotations

from pathlib import Path
import os
from unittest.mock import MagicMock

import pytest
from scripts.commands import CommandRunner
from scripts.localstack import LOCALSTACK_PORT, LocalStack, OverrideManager
from scripts.runner import InfrastructureTestRunner
from scripts.terraform_tests import TerraformTests, ExecutionMode


class TestInfrastructureTestRunner:
    """Tests for ``InfrastructureTestRunner`` orchestration."""

    def test_run_unit(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        terraform_tests = MagicMock(spec=TerraformTests)
        runner = InfrastructureTestRunner(
            root_dir=Path("/repo"),
            commands=commands,
            terraform_tests=terraform_tests,
        )

        runner.run_unit()

        commands.require.assert_called_once_with("terraform")
        terraform_tests.discover_and_run.assert_called_once_with(ExecutionMode.UNIT)

    def test_run_integration_uses_existing_localstack(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.port = LOCALSTACK_PORT
        localstack.host = "localhost"
        localstack.api_url = f"http://localhost:{LOCALSTACK_PORT}"
        localstack.can_start_container = True
        localstack.healthy.return_value = True
        localstack.image_info.return_value = ("localstack/localstack:1.0", "1.0")
        overrides = MagicMock(spec=OverrideManager)
        terraform_tests = MagicMock(spec=TerraformTests)

        runner = InfrastructureTestRunner(
            root_dir=Path("/repo"),
            commands=commands,
            localstack=localstack,
            overrides=overrides,
            terraform_tests=terraform_tests,
        )
        runner.run_integration()

        localstack.start.assert_not_called()
        localstack.wait_ready.assert_called_once()
        overrides.write.assert_called_once()
        terraform_tests.discover_and_run.assert_called_once_with(ExecutionMode.INTEGRATION)
        overrides.cleanup.assert_called_once()
        localstack.stop.assert_not_called()
        assert os.environ["AWS_ENDPOINT_URL"] == f"http://localhost:{LOCALSTACK_PORT}"

    def test_run_integration_starts_localstack_when_docker_available(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.port = LOCALSTACK_PORT
        localstack.host = "localhost"
        localstack.api_url = f"http://localhost:{LOCALSTACK_PORT}"
        localstack.can_start_container = True
        localstack.healthy.return_value = False
        localstack.image_info.return_value = ("localstack/localstack:1.0", "1.0")
        overrides = MagicMock(spec=OverrideManager)
        terraform_tests = MagicMock(spec=TerraformTests)

        runner = InfrastructureTestRunner(
            root_dir=Path("/repo"),
            commands=commands,
            localstack=localstack,
            overrides=overrides,
            terraform_tests=terraform_tests,
        )
        runner.run_integration()

        localstack.start.assert_called_once_with("localstack/localstack:1.0")
        localstack.wait_ready.assert_called_once()
        localstack.stop.assert_called_once()
        terraform_tests.discover_and_run.assert_called_once_with(ExecutionMode.INTEGRATION)
        assert os.environ["AWS_ENDPOINT_URL"] == f"http://localhost:{LOCALSTACK_PORT}"

    def test_run_integration_stops_localstack_when_cleanup_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.port = LOCALSTACK_PORT
        localstack.host = "localhost"
        localstack.api_url = f"http://localhost:{LOCALSTACK_PORT}"
        localstack.can_start_container = True
        localstack.healthy.return_value = False
        localstack.image_info.return_value = ("localstack/localstack:1.0-alt", "1.0")
        overrides = MagicMock(spec=OverrideManager)
        overrides.cleanup.side_effect = RuntimeError("cleanup failed")
        terraform_tests = MagicMock(spec=TerraformTests)

        runner = InfrastructureTestRunner(
            root_dir=Path("/repo-alt"),
            commands=commands,
            localstack=localstack,
            overrides=overrides,
            terraform_tests=terraform_tests,
        )
        with pytest.raises(RuntimeError, match="cleanup failed"):
            runner.run_integration()

        overrides.cleanup.assert_called_once()
        localstack.stop.assert_called_once()
        assert os.environ["AWS_ENDPOINT_URL"] == f"http://localhost:{LOCALSTACK_PORT}"

    def test_run_integration_waits_for_external_localstack(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.port = LOCALSTACK_PORT
        localstack.host = "localstack"
        localstack.api_url = f"http://localstack:{LOCALSTACK_PORT}"
        localstack.can_start_container = False
        localstack.healthy.return_value = False
        overrides = MagicMock(spec=OverrideManager)
        terraform_tests = MagicMock(spec=TerraformTests)

        runner = InfrastructureTestRunner(
            root_dir=Path("/repo-alt"),
            commands=commands,
            localstack=localstack,
            overrides=overrides,
            terraform_tests=terraform_tests,
        )
        runner.run_integration()

        commands.require.assert_called_once_with("terraform")
        localstack.start.assert_not_called()
        localstack.wait_ready.assert_called_once()
        localstack.stop.assert_not_called()
        terraform_tests.discover_and_run.assert_called_once_with(ExecutionMode.INTEGRATION)
        assert os.environ["AWS_ENDPOINT_URL"] == f"http://localstack:{LOCALSTACK_PORT}"
