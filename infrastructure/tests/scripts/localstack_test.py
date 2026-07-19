"""Tests for ``scripts.localstack``."""

from __future__ import annotations

import json
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from scripts.commands import CommandRunner
from scripts.errors import (
    CommandNotFoundError,
    MissingAuthTokenError,
    OverrideExistsError,
    TestRunnerError,
)
from scripts.localstack import (
    LOCALSTACK_CONTAINER_NAME,
    LOCALSTACK_PORT,
    LocalStack,
    OverrideManager,
)


def mock_info_response(
    *,
    status: int = HTTPStatus.OK,
    payload: dict | None = None,
) -> MagicMock:
    response = MagicMock()
    response.status = status
    response.read.return_value = json.dumps(payload or {}).encode("utf-8")
    return response


CUSTOM_HOST_API_URL = "http://custom-host:9999"  # NOSONAR: Test-only LocalStack HTTP.


class TestLocalStack:
    """Tests for ``LocalStack``."""

    def test_init_api_url(self) -> None:
        localstack = LocalStack(host="custom-host", port=9999)
        assert localstack.api_url == CUSTOM_HOST_API_URL

    @patch("scripts.localstack.HTTPConnection")
    def test_info_success(self, mock_connection_cls: MagicMock) -> None:
        connection = mock_connection_cls.return_value
        connection.getresponse.return_value = mock_info_response(
            payload={"version": "1.0", "is_license_activated": True}
        )
        info = LocalStack().info()
        assert info == {"version": "1.0", "is_license_activated": True}
        connection.request.assert_called_once_with("GET", "/_localstack/info")

    @patch("scripts.localstack.HTTPConnection")
    def test_info_failure(self, mock_connection_cls: MagicMock) -> None:
        connection = mock_connection_cls.return_value
        connection.getresponse.return_value = mock_info_response(status=HTTPStatus.NOT_FOUND)
        assert LocalStack().info() is None

    @patch("scripts.localstack.logger")
    @patch("scripts.localstack.HTTPConnection")
    def test_info_exception_with_log_error(
        self, mock_connection_cls: MagicMock, mock_logger: MagicMock
    ) -> None:
        mock_connection_cls.return_value.request.side_effect = OSError("Connection failed")

        assert LocalStack().info(log_error=True) is None
        mock_logger.warning.assert_called_once()

    @patch("scripts.localstack.HTTPConnection")
    def test_healthy_success(self, mock_connection_cls: MagicMock) -> None:
        connection = mock_connection_cls.return_value
        connection.getresponse.return_value = mock_info_response()
        assert LocalStack().healthy() is True

    @patch("scripts.localstack.HTTPConnection")
    def test_healthy_failure(self, mock_connection_cls: MagicMock) -> None:
        mock_connection_cls.return_value.request.side_effect = OSError("Connection refused")
        assert LocalStack().healthy() is False

    @patch("scripts.localstack.HTTPConnection")
    def test_license_activated_true(self, mock_connection_cls: MagicMock) -> None:
        connection = mock_connection_cls.return_value
        connection.getresponse.return_value = mock_info_response(
            payload={"is_license_activated": True}
        )
        assert LocalStack().license_activated() is True

    @patch("scripts.localstack.HTTPConnection")
    def test_license_activated_false(self, mock_connection_cls: MagicMock) -> None:
        connection = mock_connection_cls.return_value
        connection.getresponse.return_value = mock_info_response(
            payload={"is_license_activated": False}
        )
        assert LocalStack().license_activated() is False

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_image_info_pro(self, mock_read_text: MagicMock, mock_exists: MagicMock) -> None:
        mock_exists.return_value = True
        mock_read_text.return_value = (
            "FROM localstack/localstack-pro:2026.6.0@sha256:123456\nUSER localstack\n"
        )
        full_img, tag = LocalStack().image_info("/dummy/root")
        assert full_img == "localstack/localstack-pro:2026.6.0@sha256:123456"
        assert tag == "2026.6.0"

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_image_info_standard(self, mock_read_text: MagicMock, mock_exists: MagicMock) -> None:
        mock_exists.return_value = True
        mock_read_text.return_value = "FROM localstack/localstack:2.3.1\n"
        full_img, tag = LocalStack().image_info("/dummy/root")
        assert full_img == "localstack/localstack:2.3.1"
        assert tag == "2.3.1"

    @patch("pathlib.Path.exists")
    def test_image_info_missing_dockerfile(self, mock_exists: MagicMock) -> None:
        mock_exists.return_value = False
        localstack = LocalStack()
        with pytest.raises(TestRunnerError, match="Dockerfile not found"):
            localstack.image_info("/dummy/root")

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_image_info_no_from_line(
        self,
        mock_read_text: MagicMock,
        mock_exists: MagicMock,
    ) -> None:
        mock_exists.return_value = True
        mock_read_text.return_value = "FROM alpine:3.20\n"
        localstack = LocalStack()
        with pytest.raises(TestRunnerError, match="could not determine LocalStack image"):
            localstack.image_info("/dummy/root-1")

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_image_info_unparsable_tag(
        self,
        mock_read_text: MagicMock,
        mock_exists: MagicMock,
    ) -> None:
        mock_exists.return_value = True
        mock_read_text.return_value = "FROM localstack/localstack:\n"
        localstack = LocalStack()
        with pytest.raises(TestRunnerError, match="could not determine LocalStack image tag"):
            localstack.image_info("/dummy/root-1")

    @patch("os.environ.get")
    def test_start_success(self, mock_env: MagicMock) -> None:
        mock_env.return_value = "dummy-token"
        commands = MagicMock(spec=CommandRunner)
        localstack = LocalStack(commands)

        localstack.start("localstack/localstack:latest")

        commands.run.assert_any_call(
            "docker",
            "run",
            "-d",
            "--name",
            LOCALSTACK_CONTAINER_NAME,
            "-p",
            f"{LOCALSTACK_PORT}:{LOCALSTACK_PORT}",
            "-e",
            "ECR_ENDPOINT_STRATEGY=off",
            "-e",
            "LOCALSTACK_AUTH_TOKEN",
            "localstack/localstack:latest",
            check=True,
        )

    @patch("os.environ.get")
    def test_start_maps_host_port_to_gateway_port(self, mock_env: MagicMock) -> None:
        mock_env.return_value = "dummy-token"
        commands = MagicMock(spec=CommandRunner)
        host_port = 4567
        localstack = LocalStack(commands, port=host_port)

        localstack.start("localstack/localstack:latest-alt")

        commands.run.assert_any_call(
            "docker",
            "run",
            "-d",
            "--name",
            LOCALSTACK_CONTAINER_NAME,
            "-p",
            f"{host_port}:{LOCALSTACK_PORT}",
            "-e",
            "ECR_ENDPOINT_STRATEGY=off",
            "-e",
            "LOCALSTACK_AUTH_TOKEN",
            "localstack/localstack:latest-alt",
            check=True,
        )

    @patch("os.environ.get")
    def test_start_missing_auth_token(self, mock_env: MagicMock) -> None:
        mock_env.return_value = None
        localstack = LocalStack(MagicMock(spec=CommandRunner))
        with pytest.raises(MissingAuthTokenError):
            localstack.start("localstack/localstack:latest")

    @patch("os.environ.get")
    def test_start_docker_run_failure(self, mock_env: MagicMock) -> None:
        mock_env.return_value = "dummy-token"
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [
            MagicMock(returncode=0),
            CommandNotFoundError("docker"),
        ]
        localstack = LocalStack(commands)
        with pytest.raises(TestRunnerError, match="Error starting LocalStack container"):
            localstack.start("localstack/localstack:latest")

    def test_stop(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = LocalStack(commands)
        localstack.stop()

        assert commands.run.call_count == 2
        commands.run.assert_any_call("docker", "stop", LOCALSTACK_CONTAINER_NAME, check=False)
        commands.run.assert_any_call("docker", "rm", LOCALSTACK_CONTAINER_NAME, check=False)

    def test_wait_ready_healthy_timeout(self) -> None:
        localstack = LocalStack(MagicMock(spec=CommandRunner))
        with (
            patch.object(localstack, "healthy", return_value=False),
            patch("time.sleep") as mock_sleep,
            pytest.raises(TestRunnerError, match="failed to become healthy"),
        ):
            localstack.wait_ready()
        mock_sleep.assert_called()

    def test_wait_ready_license_timeout(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=0)
        localstack = LocalStack(commands)
        with (
            patch.object(localstack, "healthy", return_value=True),
            patch.object(localstack, "license_activated", return_value=False),
            patch("time.sleep") as mock_sleep,
            pytest.raises(TestRunnerError, match="license failed to activate"),
        ):
            localstack.wait_ready()
        mock_sleep.assert_called()
        commands.run.assert_any_call(
            "docker",
            "logs",
            "--tail",
            "30",
            LOCALSTACK_CONTAINER_NAME,
            check=False,
        )

    def test_can_start_container_when_docker_works(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=0)
        assert LocalStack(commands).can_start_container is True
        commands.run.assert_called_once_with(
            "docker",
            "info",
            check=False,
            capture_output=True,
        )

    def test_can_start_container_when_docker_missing(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = CommandNotFoundError("docker")
        assert LocalStack(commands).can_start_container is False

    def test_can_start_container_when_docker_daemon_unavailable(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=1)
        assert LocalStack(commands).can_start_container is False


class TestOverrideManager:
    """Tests for ``OverrideManager``."""

    @patch("pathlib.Path.exists")
    def test_check_absent_when_exists(self, mock_exists: MagicMock) -> None:
        mock_exists.return_value = True
        manager = OverrideManager()
        with pytest.raises(OverrideExistsError):
            manager.check_absent()

    @patch("pathlib.Path.exists")
    def test_check_absent_when_none(self, mock_exists: MagicMock) -> None:
        mock_exists.return_value = False
        OverrideManager().check_absent()

    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.mkdir")
    def test_write(self, mock_mkdir: MagicMock, mock_write_text: MagicMock) -> None:
        OverrideManager().write()
        assert mock_write_text.call_count == len(OverrideManager.OVERRIDES)
        mock_mkdir.assert_called()

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.unlink")
    def test_cleanup(self, mock_unlink: MagicMock, mock_exists: MagicMock) -> None:
        mock_exists.return_value = True
        OverrideManager().cleanup()
        assert mock_unlink.call_count == len(OverrideManager.OVERRIDES)
