"""Tests for ``scripts.deploy_runner``."""

import logging
import os
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from scripts.commands import CommandRunner
from scripts.deploy_runner import (
    LOCALSTACK_TFBACKEND,
    LOCALSTACK_TFVARS,
    InfrastructureDeployRunner,
)
from scripts.errors import RunnerError
from scripts.images import ImageManager
from scripts.localstack import LocalStack
from scripts.sync_params_runner import InfrastructureParameterSyncRunner

LOCALSTACK_ENDPOINT_URL = "http://localstack:4566"  # NOSONAR: Test-only LocalStack HTTP.
AWS_ENV_VARS = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_ENDPOINT_URL")
FAKE_CREDENTIAL = "test"


def assert_aws_env_unset() -> None:
    for var in AWS_ENV_VARS:
        assert var not in os.environ


def build_runner(
    commands: MagicMock,
    localstack: MagicMock,
    *,
    images: MagicMock | None = None,
    parameter_sync: MagicMock | None = None,
) -> InfrastructureDeployRunner:
    return InfrastructureDeployRunner(
        root_dir=Path("/repo"),
        commands=commands,
        images=images,
        localstack=localstack,
        parameter_sync=parameter_sync,
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
                    f"-var-file={LOCALSTACK_TFVARS}",
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
                    f"-backend-config={LOCALSTACK_TFBACKEND}",
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
                    f"-var-file={LOCALSTACK_TFVARS}",
                    check=False,
                ),
            ]
        )

    def test_apply_live_appends_refresh_false_when_refresh_disabled(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=0)
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        runner.apply_live(refresh=False)

        live_dir = str(Path("/repo") / "infrastructure" / "live")
        commands.run.assert_has_calls(
            [
                call(
                    "tflocal",
                    f"-chdir={live_dir}",
                    "apply",
                    "-auto-approve",
                    "-input=false",
                    f"-var-file={LOCALSTACK_TFVARS}",
                    "-refresh=false",
                    check=False,
                ),
            ]
        )

    def test_apply_live_appends_var_overrides_after_var_file(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=0)
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        runner.apply_live(
            var_overrides={"backend_image_tag": "tag-1", "frontend_image_tag": "tag-2"}
        )

        live_dir = str(Path("/repo") / "infrastructure" / "live")
        commands.run.assert_has_calls(
            [
                call(
                    "tflocal",
                    f"-chdir={live_dir}",
                    "apply",
                    "-auto-approve",
                    "-input=false",
                    f"-var-file={LOCALSTACK_TFVARS}",
                    "-var",
                    "backend_image_tag=tag-1",
                    "-var",
                    "frontend_image_tag=tag-2",
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

    def test_init_live_runs_terraform_init(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=0)
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        runner.init_live()

        live_dir = str(Path("/repo") / "infrastructure" / "live")
        commands.run.assert_called_once_with(
            "tflocal",
            f"-chdir={live_dir}",
            "init",
            f"-backend-config={LOCALSTACK_TFBACKEND}",
            "-input=false",
            "-reconfigure",
            check=False,
        )

    def test_init_live_raises_when_init_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=1)
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        with pytest.raises(RunnerError, match="terraform init failed"):
            runner.init_live()

    @patch.dict(os.environ, {}, clear=True)
    def test_deploy_uploads_nest_dump_inside_aws_env(self) -> None:
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

        def record_upload(_dump_path: Path) -> None:
            call_order.append("upload_nest_dump")
            captured["upload_aws_endpoint_url"] = os.environ["AWS_ENDPOINT_URL"]

        with (
            patch("pathlib.Path.is_file", return_value=True),
            patch.object(runner, "apply_state", side_effect=record_state),
            patch.object(runner, "apply_live", side_effect=record_live),
            patch.object(runner, "upload_nest_dump", side_effect=record_upload),
        ):
            runner.deploy()

        commands.require.assert_called_once_with("tflocal")
        localstack.wait_ready.assert_called_once()
        assert call_order == ["apply_state", "apply_live", "upload_nest_dump"]
        assert captured["AWS_ACCESS_KEY_ID"] == FAKE_CREDENTIAL
        assert captured["AWS_SECRET_ACCESS_KEY"] == FAKE_CREDENTIAL
        assert captured["AWS_ENDPOINT_URL"] == LOCALSTACK_ENDPOINT_URL
        assert captured["upload_aws_endpoint_url"] == LOCALSTACK_ENDPOINT_URL
        assert_aws_env_unset()

    def test_deploy_propagates_wait_ready_failure(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.wait_ready.side_effect = RunnerError("localstack down")
        runner = build_runner(commands, localstack)

        with pytest.raises(RunnerError, match="localstack down"):
            runner.deploy()

        commands.run.assert_not_called()

    def test_deploy_raises_when_nest_dump_is_missing(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        runner = build_runner(commands, localstack)

        with (
            patch("pathlib.Path.is_file", return_value=False),
            pytest.raises(RunnerError, match="not found"),
        ):
            runner.deploy()

        localstack.wait_ready.assert_called_once()
        commands.run.assert_not_called()

    def test_read_live_output_returns_stripped_value(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=0, stdout="bucket-name\n")
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        assert runner.read_live_output("fixtures_bucket_name") == "bucket-name"

    def test_read_live_output_raises_when_output_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=1, stderr="no state")
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        with pytest.raises(RunnerError, match="terraform output failed"):
            runner.read_live_output("fixtures_bucket_name")

    def test_upload_nest_dump_reads_bucket_and_copies_dump(self, tmp_path: Path) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [
            MagicMock(returncode=0, stdout="nest-production-fixtures-abcd\n"),
            MagicMock(returncode=0),
        ]
        runner = build_runner(commands, MagicMock(spec=LocalStack))
        dump_path = tmp_path / "nest.dump"

        runner.upload_nest_dump(dump_path)

        live_dir = str(Path("/repo") / "infrastructure" / "live")
        commands.run.assert_has_calls(
            [
                call(
                    "tflocal",
                    f"-chdir={live_dir}",
                    "output",
                    "-raw",
                    "fixtures_bucket_name",
                    capture_output=True,
                    check=False,
                ),
                call(
                    "awslocal",
                    "s3",
                    "cp",
                    str(dump_path),
                    "s3://nest-production-fixtures-abcd/nest.dump",
                    capture_output=True,
                    check=False,
                ),
            ]
        )

    def test_upload_nest_dump_raises_when_copy_fails(self, tmp_path: Path) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [
            MagicMock(returncode=0, stdout="nest-production-fixtures-abcd\n"),
            MagicMock(returncode=1, stderr="bucket missing"),
        ]
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        with pytest.raises(RunnerError, match=r"upload to s3://nest-production-fixtures-abcd"):
            runner.upload_nest_dump(tmp_path / "nest.dump")

    def test_push_images_logs_in_and_builds_and_pushes_each_service(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        images = MagicMock(spec=ImageManager)
        runner = build_runner(commands, MagicMock(spec=LocalStack), images=images)

        result = runner.push_images()

        images.login.assert_called_once_with()
        assert set(result) == {"backend", "frontend"}
        tag = result["backend"]
        assert result["frontend"] == tag
        for service in ("backend", "frontend"):
            images.build.assert_any_call(service, tag)
            images.push.assert_any_call(service, tag)

    @patch.dict(os.environ, {}, clear=True)
    def test_refresh_pushes_images_and_applies_live_inside_aws_env(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.api_url = LOCALSTACK_ENDPOINT_URL
        images = MagicMock(spec=ImageManager)
        parameter_sync = MagicMock(spec=InfrastructureParameterSyncRunner)
        runner = build_runner(commands, localstack, images=images, parameter_sync=parameter_sync)

        tag = "1735000000"
        call_order: list[str] = []
        captured: dict[str, str] = {}

        def record_live(**_kwargs) -> None:
            call_order.append("apply_live")
            for var in AWS_ENV_VARS:
                captured[var] = os.environ[var]

        def record_sync() -> None:
            call_order.append("sync_deployment_endpoints")
            for var in AWS_ENV_VARS:
                captured[f"sync_{var}"] = os.environ[var]

        parameter_sync.sync_deployment_endpoints.side_effect = record_sync

        with (
            patch.object(runner, "init_live") as mock_init,
            patch.object(
                runner,
                "push_images",
                return_value={"backend": tag, "frontend": tag},
            ) as mock_push,
            patch.object(runner, "apply_live", side_effect=record_live) as mock_live,
        ):
            runner.refresh()

        commands.require.assert_called_once_with("tflocal")
        localstack.wait_ready.assert_called_once()
        mock_init.assert_called_once_with()
        mock_push.assert_called_once_with()
        mock_live.assert_called_once_with(
            refresh=False,
            var_overrides={"backend_image_tag": tag, "frontend_image_tag": tag},
        )
        parameter_sync.sync_deployment_endpoints.assert_called_once_with()
        assert call_order == ["apply_live", "sync_deployment_endpoints"]
        assert captured["AWS_ACCESS_KEY_ID"] == FAKE_CREDENTIAL
        assert captured["AWS_SECRET_ACCESS_KEY"] == FAKE_CREDENTIAL
        assert captured["AWS_ENDPOINT_URL"] == LOCALSTACK_ENDPOINT_URL
        assert captured["sync_AWS_ENDPOINT_URL"] == LOCALSTACK_ENDPOINT_URL
        assert_aws_env_unset()

    def test_refresh_propagates_wait_ready_failure(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.wait_ready.side_effect = RunnerError("localstack down")
        runner = build_runner(commands, localstack)

        with pytest.raises(RunnerError, match="localstack down"):
            runner.refresh()

        commands.run.assert_not_called()

    def test_refresh_skips_nest_dump_steps(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.api_url = LOCALSTACK_ENDPOINT_URL
        images = MagicMock(spec=ImageManager)
        parameter_sync = MagicMock(spec=InfrastructureParameterSyncRunner)
        runner = build_runner(commands, localstack, images=images, parameter_sync=parameter_sync)

        with (
            patch.object(runner, "init_live"),
            patch.object(runner, "push_images", return_value={"backend": "t", "frontend": "t"}),
            patch.object(runner, "apply_live"),
            patch.object(runner, "upload_nest_dump") as mock_upload,
        ):
            runner.refresh()

        mock_upload.assert_not_called()
        parameter_sync.sync_deployment_endpoints.assert_called_once_with()
