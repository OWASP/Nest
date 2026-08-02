"""Tests for ``scripts.provision``."""

from __future__ import annotations

import base64
import os
import re
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.commands import CommandRunner
from scripts.errors import CommandNotFoundError, InfrastructureError
from scripts.localstack import LocalStack
from scripts.provision import (
    FIXTURES_OBJECT_KEY,
    OVERRIDE_FILE,
    ProvisionInfra,
    _bool,
)


def build_provisioner(
    tmp_path: Path,
    commands: MagicMock | None = None,
    localstack: MagicMock | None = None,
) -> ProvisionInfra:
    provisioner = ProvisionInfra(
        commands or MagicMock(spec=CommandRunner),
        localstack=localstack or MagicMock(spec=LocalStack),
    )
    provisioner.root_dir = tmp_path
    provisioner.infra_dir = tmp_path / "infrastructure"
    provisioner.live_dir = provisioner.infra_dir / "live"
    provisioner.env_path = provisioner.infra_dir / ".env"
    return provisioner


class TestBool:
    """Tests for ``_bool``."""

    @pytest.mark.parametrize("value", ["true", "True", "TRUE", '"true"'])
    def test_true_values(self, value: str) -> None:
        assert _bool(value) is True

    @pytest.mark.parametrize("value", ["false", "False", "FALSE", '"false"'])
    def test_false_values(self, value: str) -> None:
        assert _bool(value) is False

    def test_invalid_value(self) -> None:
        with pytest.raises(InfrastructureError, match="Boolean"):
            _bool("yes")


class TestProvisionInfra:
    """Tests for ``ProvisionInfra``."""

    def test_image_tag_with_git_sha(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = subprocess.CompletedProcess([], 0, stdout="abc123\n")
        provisioner = ProvisionInfra(commands, localstack=MagicMock(spec=LocalStack))

        tag = provisioner._image_tag()

        assert tag.startswith("abc123-")
        commands.run.assert_called_once_with(
            "git", "rev-parse", "--short", "HEAD", capture_output=True, check=False
        )

    def test_image_tag_falls_back_to_timestamp_when_git_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = subprocess.CompletedProcess([], 1, stdout="")
        provisioner = ProvisionInfra(commands, localstack=MagicMock(spec=LocalStack))

        assert re.fullmatch(r"\d{14}", provisioner._image_tag())

    def test_image_tag_falls_back_when_git_missing(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = CommandNotFoundError("git")
        provisioner = ProvisionInfra(commands, localstack=MagicMock(spec=LocalStack))

        assert re.fullmatch(r"\d{14}", provisioner._image_tag())

    @patch.dict(os.environ, {"DB_PASSWORD": "existing-password"}, clear=True)
    def test_db_password_reads_environment(self, tmp_path: Path) -> None:
        provisioner = build_provisioner(tmp_path)

        assert provisioner._db_password() == "existing-password"
        assert not provisioner.env_path.exists()

    @patch.dict(os.environ, {}, clear=True)
    def test_db_password_generates_and_persists(self, tmp_path: Path) -> None:
        provisioner = build_provisioner(tmp_path)

        with patch("scripts.provision.secrets.token_urlsafe", return_value="generated-password"):
            password = provisioner._db_password()

        assert password == "generated-password"  # noqa: S105
        assert "DB_PASSWORD=generated-password" in provisioner.env_path.read_text(encoding="utf-8")

    @patch.dict(
        os.environ,
        {
            "ENVIRONMENT": "local",
            "DOMAIN_NAME": "example.com",
            "ENABLE_CRON_TASKS": "true",
            "FORCE_NEW_DEPLOYMENT": "false",
        },
        clear=True,
    )
    def test_tfvars(self, tmp_path: Path) -> None:
        provisioner = build_provisioner(tmp_path)

        tfvars = provisioner.tfvars("tag-1", "pw")

        assert tfvars == {
            "environment": "local",
            "backend_image_tag": "tag-1",
            "frontend_image_tag": "tag-1",
            "django_configuration": "Local",
            "django_settings_module": "settings.local",
            "domain_name": "example.com",
            "enable_cron_tasks": True,
            "force_new_deployment": False,
            "db_password": "pw",
            "db_deletion_protection": False,
            "db_skip_final_snapshot": True,
            "enable_nat_gateway": False,
            "django_redis_use_tls": False,
            "django_redis_auth_enabled": False,
        }

    @patch.dict(os.environ, {}, clear=True)
    def test_tf_env(self, tmp_path: Path) -> None:
        provisioner = build_provisioner(tmp_path)

        tf_env = provisioner._tf_env(
            {
                "enable_cron_tasks": True,
                "force_new_deployment": False,
                "domain_name": "localhost",
                "db_password": "pw",
            }
        )

        assert tf_env == {
            "TF_VAR_enable_cron_tasks": "true",
            "TF_VAR_force_new_deployment": "false",
            "TF_VAR_domain_name": "localhost",
            "TF_VAR_db_password": "pw",
        }

    def test_terraform_apply_passes_tf_env(self, tmp_path: Path) -> None:
        commands = MagicMock(spec=CommandRunner)
        provisioner = build_provisioner(tmp_path, commands=commands)
        tfvars = {"environment": "local", "enable_cron_tasks": True}

        with patch.object(
            ProvisionInfra, "_tf_env", return_value={"TF_VAR_environment": "local"}
        ) as mock_tf_env:
            provisioner._terraform_apply(tfvars)

        mock_tf_env.assert_called_once_with(tfvars)
        commands.run.assert_called_once_with(
            "tflocal",
            "apply",
            "-auto-approve",
            cwd=provisioner.live_dir,
            env={"TF_VAR_environment": "local"},
            check=True,
        )

    def test_remove_stale_override(self, tmp_path: Path) -> None:
        provisioner = build_provisioner(tmp_path)
        override = provisioner.live_dir / OVERRIDE_FILE
        override.parent.mkdir(parents=True, exist_ok=True)
        override.write_text("stale", encoding="utf-8")

        provisioner._remove_stale_override()

        assert not override.exists()
        provisioner._remove_stale_override()

    def test_terraform_outputs(self, tmp_path: Path) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = subprocess.CompletedProcess(
            [], 0, stdout='{"a": {"value": "x"}, "b": {"value": 2}}'
        )
        provisioner = ProvisionInfra(commands, localstack=MagicMock(spec=LocalStack))

        assert provisioner._terraform_outputs() == {"a": "x", "b": 2}
        commands.run.assert_called_once_with(
            "tflocal",
            "output",
            "-json",
            cwd=provisioner.live_dir,
            capture_output=True,
            check=True,
        )

    def test_terraform_outputs_invalid_json(self, tmp_path: Path) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = subprocess.CompletedProcess([], 0, stdout="not json")
        provisioner = ProvisionInfra(commands, localstack=MagicMock(spec=LocalStack))

        with pytest.raises(InfrastructureError, match="tflocal output"):
            provisioner._terraform_outputs()

    def test_upload_fixtures_existing_dump(self, tmp_path: Path) -> None:
        provisioner = build_provisioner(tmp_path)
        dump_path = tmp_path / "backend" / "data" / FIXTURES_OBJECT_KEY
        dump_path.parent.mkdir(parents=True, exist_ok=True)
        dump_path.write_text("dump", encoding="utf-8")
        s3 = MagicMock()

        with patch("scripts.provision.aws_client", return_value=s3) as mock_aws_client:
            provisioner._upload_fixtures("fixtures-bucket")

        mock_aws_client.assert_called_once_with("s3", localstack=provisioner.localstack)
        s3.upload_file.assert_called_once_with(
            str(dump_path), "fixtures-bucket", FIXTURES_OBJECT_KEY
        )

    def test_upload_fixtures_fetches_missing_dump(self, tmp_path: Path) -> None:
        provisioner = build_provisioner(tmp_path)

        with (
            patch.object(ProvisionInfra, "_fetch_nest_dump") as mock_fetch,
            patch("scripts.provision.aws_client", return_value=MagicMock()),
        ):
            provisioner._upload_fixtures("fixtures-bucket")

        mock_fetch.assert_called_once()

    def test_fetch_nest_dump(self, tmp_path: Path) -> None:
        commands = MagicMock(spec=CommandRunner)
        provisioner = build_provisioner(tmp_path, commands=commands)

        provisioner._fetch_nest_dump()

        commands.run.assert_called_once_with(
            "docker",
            "compose",
            "-f",
            "docker-compose/e2e/compose.yaml",
            "run",
            "--no-deps",
            "--rm",
            "backend",
            "python",
            "-m",
            "scripts.fetch_nest_dump",
            cwd=provisioner.root_dir,
            check=True,
        )

    def test_docker_login(self, tmp_path: Path) -> None:
        ecr = MagicMock()
        token = base64.b64encode(b"AWS:supersecret").decode("utf-8")
        ecr.get_authorization_token.return_value = {
            "authorizationData": [{"authorizationToken": token}]
        }
        commands = MagicMock(spec=CommandRunner)
        provisioner = build_provisioner(tmp_path, commands=commands)

        with patch("scripts.provision.aws_client", return_value=ecr) as mock_aws_client:
            provisioner._docker_login("localhost:4566")

        mock_aws_client.assert_called_once_with("ecr", localstack=provisioner.localstack)
        commands.run.assert_called_once_with(
            "docker",
            "login",
            "--username",
            "AWS",
            "--password-stdin",
            "localhost:4566",
            input_data="supersecret",
            check=True,
        )

    def test_push_images(self, tmp_path: Path) -> None:
        provisioner = build_provisioner(tmp_path)

        with (
            patch.object(ProvisionInfra, "_docker_login") as mock_login,
            patch.object(ProvisionInfra, "_build_backend_image") as mock_backend,
            patch.object(ProvisionInfra, "_build_frontend_image") as mock_frontend,
        ):
            provisioner._push_images("localhost:4566/backend", "localhost:4566/frontend", "tag-1")

        mock_login.assert_called_once_with("localhost:4566")
        mock_backend.assert_called_once_with("localhost:4566/backend", "tag-1")
        mock_frontend.assert_called_once_with("localhost:4566/frontend", "tag-1")

    def test_build_backend_image(self, tmp_path: Path) -> None:
        commands = MagicMock(spec=CommandRunner)
        provisioner = build_provisioner(tmp_path, commands=commands)

        provisioner._build_backend_image("localhost:4566/backend", "tag-1")

        commands.run.assert_any_call(
            "docker",
            "build",
            "--target",
            "backend",
            "-f",
            str(tmp_path / "docker" / "backend" / "Dockerfile"),
            "-t",
            "localhost:4566/backend:tag-1",
            str(tmp_path / "backend"),
            check=True,
        )
        commands.run.assert_any_call("docker", "push", "localhost:4566/backend:tag-1", check=True)

    def test_build_frontend_image(self, tmp_path: Path) -> None:
        commands = MagicMock(spec=CommandRunner)
        provisioner = build_provisioner(tmp_path, commands=commands)

        provisioner._build_frontend_image("localhost:4566/frontend", "tag-1")

        commands.run.assert_any_call(
            "docker",
            "build",
            "-f",
            str(tmp_path / "docker" / "frontend" / "Dockerfile"),
            "--build-arg",
            "ENV_FILE=.env.localstack",
            "--build-arg",
            "FORCE_STANDALONE=yes",
            "-t",
            "localhost:4566/frontend:tag-1",
            str(tmp_path / "frontend"),
            check=True,
        )
        commands.run.assert_any_call("docker", "push", "localhost:4566/frontend:tag-1", check=True)

    def test_run_executes_workflow(self, tmp_path: Path) -> None:
        outputs = {
            "fixtures_bucket_name": "fixtures-bucket",
            "backend_ecr_repository_url": "localhost:4566/backend",
            "frontend_ecr_repository_url": "localhost:4566/frontend",
        }
        tfvars = {
            "environment": "local",
            "domain_name": "localhost",
            "enable_cron_tasks": False,
        }

        with (
            patch.object(ProvisionInfra, "_image_tag", return_value="abc123-20260101"),
            patch.object(ProvisionInfra, "_db_password", return_value="pw"),
            patch.object(ProvisionInfra, "tfvars", return_value=tfvars),
            patch.object(ProvisionInfra, "_remove_stale_override") as mock_remove,
            patch.object(ProvisionInfra, "_terraform_init") as mock_init,
            patch.object(ProvisionInfra, "_terraform_apply") as mock_apply,
            patch.object(
                ProvisionInfra, "_terraform_outputs", return_value=outputs
            ) as mock_outputs,
            patch.object(ProvisionInfra, "_upload_fixtures") as mock_upload,
            patch.object(ProvisionInfra, "_push_images") as mock_push,
            patch.object(ProvisionInfra, "_log_summary") as mock_summary,
        ):
            commands = MagicMock(spec=CommandRunner)
            localstack = MagicMock(spec=LocalStack)
            provisioner = ProvisionInfra(commands, localstack=localstack)
            provisioner.run()

        commands.require.assert_any_call("tflocal")
        commands.require.assert_any_call("docker")
        localstack.wait_ready.assert_called_once()
        mock_remove.assert_called_once()
        mock_init.assert_called_once()
        mock_apply.assert_called_once_with(tfvars)
        mock_outputs.assert_called_once()
        mock_upload.assert_called_once_with("fixtures-bucket")
        mock_push.assert_called_once_with(
            "localhost:4566/backend", "localhost:4566/frontend", "abc123-20260101"
        )
        mock_summary.assert_called_once_with(outputs, "abc123-20260101")

    def test_run_requires_prerequisites(self, tmp_path: Path) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.require.side_effect = CommandNotFoundError("docker")
        localstack = MagicMock(spec=LocalStack)
        provisioner = ProvisionInfra(commands, localstack=localstack)

        with pytest.raises(CommandNotFoundError, match="docker"):
            provisioner.run()

        localstack.wait_ready.assert_not_called()
