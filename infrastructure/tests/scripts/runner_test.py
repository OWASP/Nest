"""Tests for ``scripts.runner``."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from scripts.commands import CommandRunner
from scripts.localstack import LOCALSTACK_PORT, LocalStack, OverrideManager
from scripts.runner import InfrastructureTestRunner
from scripts.terraform_tests import TerraformTests


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
        terraform_tests.discover_and_run.assert_called_once_with("unit")

    def test_run_integration_uses_existing_localstack(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.port = LOCALSTACK_PORT
        localstack.host = "localhost"
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
        overrides.write.assert_called_once()
        terraform_tests.discover_and_run.assert_called_once_with("integration")
        overrides.cleanup.assert_called_once()
        localstack.stop.assert_not_called()

    def test_run_integration_starts_localstack_when_docker_available(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.port = LOCALSTACK_PORT
        localstack.host = "localhost"
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
        terraform_tests.discover_and_run.assert_called_once_with("integration")

    def test_run_integration_waits_for_external_localstack(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.port = LOCALSTACK_PORT
        localstack.host = "localstack"
        localstack.can_start_container = False
        localstack.healthy.return_value = False
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

        commands.require.assert_called_once_with("terraform")
        localstack.start.assert_not_called()
        localstack.wait_ready.assert_called_once()
        localstack.stop.assert_not_called()
        terraform_tests.discover_and_run.assert_called_once_with("integration")
