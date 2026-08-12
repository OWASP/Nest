"""Tests for ``scripts.dev``."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from scripts.dev import LocalInfrastructureRunner, main
from scripts.errors import MissingEnvVarError
from scripts.localstack import LocalStack

AUTH_TOKEN = "test-auth-token"  # noqa: S105


class TestLocalInfrastructureRunner:
    """Tests for ``LocalInfrastructureRunner`` orchestration."""

    @staticmethod
    def build_runner(localstack: MagicMock) -> LocalInfrastructureRunner:
        return LocalInfrastructureRunner(localstack=localstack)

    @patch.dict(os.environ, {"LOCALSTACK_AUTH_TOKEN": ""})
    def test_start_localstack_requires_auth_token(self) -> None:
        localstack = MagicMock(spec=LocalStack)
        runner = self.build_runner(localstack)

        with pytest.raises(MissingEnvVarError, match="LOCALSTACK_AUTH_TOKEN"):
            runner.start_localstack()

        localstack.start.assert_not_called()
        localstack.wait_ready.assert_not_called()

    @patch.dict(os.environ, {"LOCALSTACK_AUTH_TOKEN": AUTH_TOKEN})
    def test_start_localstack_is_idempotent(self) -> None:
        localstack = MagicMock(spec=LocalStack)
        localstack.healthy.return_value = True
        localstack.api_url = "http://localhost:4566"  # NOSONAR: Test-only LocalStack HTTP.
        runner = self.build_runner(localstack)

        runner.start_localstack()

        localstack.start.assert_not_called()
        localstack.wait_ready.assert_not_called()

    @patch.dict(os.environ, {"LOCALSTACK_AUTH_TOKEN": AUTH_TOKEN})
    def test_start_localstack_starts_container(self) -> None:
        localstack = MagicMock(spec=LocalStack)
        localstack.healthy.return_value = False
        localstack.image_info.return_value = ("localstack/localstack:1.0", "1.0")
        runner = self.build_runner(localstack)

        runner.start_localstack()

        localstack.image_info.assert_called_once_with(runner.root_dir)
        localstack.start.assert_called_once_with("localstack/localstack:1.0")
        localstack.wait_ready.assert_called_once()

    def test_stop_localstack(self) -> None:
        localstack = MagicMock(spec=LocalStack)
        runner = self.build_runner(localstack)

        runner.stop_localstack()

        localstack.stop.assert_called_once()

    def test_provision_infra(self) -> None:
        localstack = MagicMock(spec=LocalStack)
        runner = self.build_runner(localstack)
        runner.provisioner = MagicMock()

        runner.provision_infra()

        runner.provisioner.run.assert_called_once()

    def test_load_env_params(self) -> None:
        localstack = MagicMock(spec=LocalStack)
        runner = self.build_runner(localstack)
        runner.loadenv = MagicMock()

        runner.load_env_params(dry_run=True, overwrite=True)

        runner.loadenv.upload.assert_called_once_with(dry_run=True, overwrite=True)

    def test_deploy_services(self) -> None:
        localstack = MagicMock(spec=LocalStack)
        runner = self.build_runner(localstack)
        runner.deployer = MagicMock()

        runner.deploy_services()

        runner.deployer.run.assert_called_once()


class TestMain:
    """Tests for the ``main`` command dispatcher."""

    @patch("sys.argv", ["scripts.dev", "start-localstack"])
    @patch("scripts.dev.LocalInfrastructureRunner")
    def test_dispatches_start_localstack(self, mock_runner_class: MagicMock) -> None:
        main()

        mock_runner_class.return_value.start_localstack.assert_called_once()

    @patch("sys.argv", ["scripts.dev", "stop-localstack"])
    @patch("scripts.dev.LocalInfrastructureRunner")
    def test_dispatches_stop_localstack(self, mock_runner_class: MagicMock) -> None:
        main()

        mock_runner_class.return_value.stop_localstack.assert_called_once()

    @patch("sys.argv", ["scripts.dev", "provision-infra"])
    @patch("scripts.dev.LocalInfrastructureRunner")
    def test_dispatches_provision_infra(self, mock_runner_class: MagicMock) -> None:
        main()

        mock_runner_class.return_value.provision_infra.assert_called_once()

    @patch("sys.argv", ["scripts.dev", "load-env-params"])
    @patch("scripts.dev.LocalInfrastructureRunner")
    def test_dispatches_load_env_params(self, mock_runner_class: MagicMock) -> None:
        main()

        mock_runner_class.return_value.load_env_params.assert_called_once_with(
            dry_run=False, overwrite=False
        )

    @patch("sys.argv", ["scripts.dev", "load-env-params", "--dry-run", "--overwrite"])
    @patch("scripts.dev.LocalInfrastructureRunner")
    def test_dispatches_load_env_params_with_flags(self, mock_runner_class: MagicMock) -> None:
        main()

        mock_runner_class.return_value.load_env_params.assert_called_once_with(
            dry_run=True, overwrite=True
        )

    @patch("sys.argv", ["scripts.dev", "deploy-services"])
    @patch("scripts.dev.LocalInfrastructureRunner")
    def test_dispatches_deploy_services(self, mock_runner_class: MagicMock) -> None:
        main()

        mock_runner_class.return_value.deploy_services.assert_called_once()

    @patch("sys.argv", ["scripts.dev", "start-localstack"])
    @patch("scripts.dev.LocalInfrastructureRunner")
    def test_exits_with_error_message(
        self, mock_runner_class: MagicMock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        mock_runner_class.return_value.start_localstack.side_effect = MissingEnvVarError(
            "LOCALSTACK_AUTH_TOKEN"
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        assert "LOCALSTACK_AUTH_TOKEN" in capsys.readouterr().err

    @patch("sys.argv", ["scripts.dev", "unknown"])
    @patch("scripts.dev.LocalInfrastructureRunner")
    def test_rejects_unknown_command(self, mock_runner_class: MagicMock) -> None:
        with pytest.raises(SystemExit):
            main()

        mock_runner_class.assert_not_called()
