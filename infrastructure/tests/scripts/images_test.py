"""Tests for ``scripts.images``."""

from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

from scripts.commands import CommandRunner
from scripts.constants import SOURCE_REPO_DIR
from scripts.errors import RunnerError
from scripts.images import IMAGE_CONFIG, ImageManager
from scripts.localstack import LocalStack

REGISTRY_HOST = "000000000000.dkr.ecr.us-east-1.amazonaws.com"
BACKEND_REPO_URL = f"{REGISTRY_HOST}/nest-production-backend"


def build_manager(commands: MagicMock | None = None) -> ImageManager:
    return ImageManager(
        root_dir=Path("/repo-root"),
        commands=commands or MagicMock(spec=CommandRunner),
        localstack=MagicMock(spec=LocalStack),
    )


class TestImageConfig:
    """Tests for the ``IMAGE_CONFIG`` module-level mapping."""

    def test_backend_config(self) -> None:
        assert IMAGE_CONFIG["backend"] == {"target": "backend", "buildargs": None}

    def test_frontend_config(self) -> None:
        assert IMAGE_CONFIG["frontend"] == {
            "target": None,
            "buildargs": {"ENV_FILE": ".env.localstack"},
        }


class TestImageManager:
    """Tests for ``ImageManager`` behavior."""

    def test_build_shells_out_to_docker_buildx_with_backend_config(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [
            MagicMock(returncode=0, stdout=BACKEND_REPO_URL),
            MagicMock(returncode=0),
        ]
        manager = build_manager(commands=commands)

        manager.build("backend", "tag-1")

        assert commands.run.call_args_list[-1] == call(
            "docker",
            "buildx",
            "build",
            "--load",
            "--file",
            str(SOURCE_REPO_DIR / "docker" / "backend" / "Dockerfile"),
            "--tag",
            f"{BACKEND_REPO_URL}:tag-1",
            "--target",
            "backend",
            str(SOURCE_REPO_DIR / "backend"),
        )

    def test_build_shells_out_to_docker_buildx_with_frontend_config(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        frontend_repo = f"{REGISTRY_HOST}/nest-production-frontend"
        commands.run.side_effect = [
            MagicMock(returncode=0, stdout=frontend_repo),
            MagicMock(returncode=0),
        ]
        manager = build_manager(commands=commands)

        manager.build("frontend", "tag-1")

        assert commands.run.call_args_list[-1] == call(
            "docker",
            "buildx",
            "build",
            "--load",
            "--file",
            str(SOURCE_REPO_DIR / "docker" / "frontend" / "Dockerfile"),
            "--tag",
            f"{frontend_repo}:tag-1",
            "--build-arg",
            f"ENV_FILE={IMAGE_CONFIG['frontend']['buildargs']['ENV_FILE']}",
            str(SOURCE_REPO_DIR / "frontend"),
        )

    def test_build_raises_when_docker_build_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [
            MagicMock(returncode=0, stdout=BACKEND_REPO_URL),
            MagicMock(returncode=1),
        ]
        manager = build_manager(commands=commands)

        with pytest.raises(RunnerError, match="docker build failed for backend"):
            manager.build("backend", "tag-1")

    def test_login_pipes_awslocal_password_into_docker_login(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [
            MagicMock(returncode=0, stdout="password-123\n"),
            MagicMock(returncode=0, stdout=BACKEND_REPO_URL),
            MagicMock(returncode=0),
        ]
        manager = build_manager(commands=commands)

        manager.login()

        commands.require.assert_any_call("awslocal")
        commands.require.assert_any_call("docker")
        assert commands.run.call_args_list[0] == call(
            "awslocal",
            "ecr",
            "get-login-password",
            capture_output=True,
        )
        assert commands.run.call_args_list[-1] == call(
            "docker",
            "login",
            "--username",
            "AWS",
            "--password-stdin",
            REGISTRY_HOST,
            capture_output=True,
            stdin_input="password-123\n",
        )

    def test_login_raises_when_awslocal_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=1, stdout="", stderr="boom")
        manager = build_manager(commands=commands)

        with pytest.raises(RunnerError, match="awslocal ecr get-login-password"):
            manager.login()

    def test_login_raises_when_docker_login_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [
            MagicMock(returncode=0, stdout="password-123\n"),
            MagicMock(returncode=0, stdout=BACKEND_REPO_URL),
            MagicMock(returncode=1, stderr="unauthorized"),
        ]
        manager = build_manager(commands=commands)

        with pytest.raises(RunnerError, match="docker login failed"):
            manager.login()

    def test_push_shells_out_to_docker_push(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [
            MagicMock(returncode=0, stdout=BACKEND_REPO_URL),
            MagicMock(returncode=0),
        ]
        manager = build_manager(commands=commands)

        manager.push("backend", "tag-1")

        assert commands.run.call_args_list[-1] == call(
            "docker",
            "push",
            f"{BACKEND_REPO_URL}:tag-1",
        )

    def test_push_raises_when_docker_push_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [
            MagicMock(returncode=0, stdout=BACKEND_REPO_URL),
            MagicMock(returncode=1),
        ]
        manager = build_manager(commands=commands)

        with pytest.raises(RunnerError, match="docker push failed for backend"):
            manager.push("backend", "tag-1")

    def test_registry_url_derives_host_from_backend_repository(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=0, stdout=BACKEND_REPO_URL)
        manager = build_manager(commands=commands)

        assert manager.registry_url() == REGISTRY_HOST

    def test_repository_url_shells_out_to_terraform_output(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=0, stdout=f"{BACKEND_REPO_URL}\n")
        manager = build_manager(commands=commands)

        result = manager.repository_url("backend")

        commands.require.assert_called_once_with("terraform")
        live_dir = str(Path("/repo-root") / "infrastructure" / "live")
        commands.run.assert_called_once_with(
            "terraform",
            f"-chdir={live_dir}",
            "output",
            "-raw",
            "backend_ecr_repository_url",
            capture_output=True,
        )
        assert result == BACKEND_REPO_URL

    def test_repository_url_raises_when_terraform_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=1, stdout="", stderr="err")
        manager = build_manager(commands=commands)

        with pytest.raises(RunnerError, match="terraform output backend_ecr_repository_url"):
            manager.repository_url("backend")
