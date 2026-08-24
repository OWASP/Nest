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
) -> InfrastructureDeployRunner:
    return InfrastructureDeployRunner(
        root_dir=Path("/repo"),
        commands=commands,
        images=images,
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
    def test_refresh_pushes_images_applies_live_and_restarts_service_tasks(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.api_url = LOCALSTACK_ENDPOINT_URL
        images = MagicMock(spec=ImageManager)
        runner = build_runner(commands, localstack, images=images)

        tag = "1735000000"
        captured: dict[str, str] = {}

        def record_live(**_kwargs) -> None:
            for var in AWS_ENV_VARS:
                captured[var] = os.environ[var]

        with (
            patch.object(runner, "init_live") as mock_init,
            patch.object(
                runner,
                "push_images",
                return_value={"backend": tag, "frontend": tag},
            ) as mock_push,
            patch.object(runner, "apply_live", side_effect=record_live) as mock_live,
            patch.object(runner, "restart_service_task") as mock_restart,
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
        mock_restart.assert_any_call(
            cluster="nest-production-backend-cluster",
            service="nest-production-backend-service",
        )
        mock_restart.assert_any_call(
            cluster="nest-production-frontend-cluster",
            service="nest-production-frontend-service",
        )
        assert captured["AWS_ACCESS_KEY_ID"] == FAKE_CREDENTIAL
        assert captured["AWS_SECRET_ACCESS_KEY"] == FAKE_CREDENTIAL
        assert captured["AWS_ENDPOINT_URL"] == LOCALSTACK_ENDPOINT_URL
        assert_aws_env_unset()

    def test_run_task_shells_out_to_awslocal_and_returns_arn(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(
            returncode=0,
            stdout="arn:aws:ecs:us-east-1:000000000000:task/cluster/abc-123\n",
        )
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        arn = runner.run_task(
            cluster="c",
            task_definition="td",
            subnets=["sub-1", "sub-2"],
            security_groups=["sg-1"],
        )

        commands.require.assert_called_once_with("awslocal")
        commands.run.assert_called_once_with(
            "awslocal",
            "ecs",
            "run-task",
            "--cluster",
            "c",
            "--task-definition",
            "td",
            "--launch-type",
            "FARGATE",
            "--network-configuration",
            "awsvpcConfiguration={subnets=[sub-1,sub-2],securityGroups=[sg-1],assignPublicIp=ENABLED}",
            "--query",
            "tasks[0].taskArn",
            "--output",
            "text",
            capture_output=True,
        )
        assert arn == "arn:aws:ecs:us-east-1:000000000000:task/cluster/abc-123"

    def test_run_task_raises_when_awslocal_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=1, stderr="boom")
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        with pytest.raises(RunnerError, match="awslocal ecs run-task failed"):
            runner.run_task(
                cluster="c",
                task_definition="td",
                subnets=["s"],
                security_groups=["sg"],
            )

    def test_stop_cluster_tasks_lists_and_stops_each(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [
            MagicMock(returncode=0, stdout="arn-1\tarn-2\n"),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
        ]
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        runner.stop_cluster_tasks("c")

        commands.require.assert_called_once_with("awslocal")
        assert commands.run.call_args_list[0] == call(
            "awslocal",
            "ecs",
            "list-tasks",
            "--cluster",
            "c",
            "--desired-status",
            "RUNNING",
            "--query",
            "taskArns",
            "--output",
            "text",
            capture_output=True,
        )
        assert commands.run.call_args_list[1] == call(
            "awslocal",
            "ecs",
            "stop-task",
            "--cluster",
            "c",
            "--task",
            "arn-1",
            capture_output=True,
        )
        assert commands.run.call_args_list[2] == call(
            "awslocal",
            "ecs",
            "stop-task",
            "--cluster",
            "c",
            "--task",
            "arn-2",
            capture_output=True,
        )

    def test_stop_cluster_tasks_no_op_when_no_running_tasks(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=0, stdout="\n")
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        runner.stop_cluster_tasks("c")

        assert commands.run.call_count == 1

    def test_restart_service_task_stops_then_runs_new_task(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        runner = build_runner(commands, MagicMock(spec=LocalStack))

        describe_json = (
            '{"services":[{"taskDefinition":"td-arn",'
            '"networkConfiguration":{"awsvpcConfiguration":'
            '{"subnets":["sub-1"],"securityGroups":["sg-1"],"assignPublicIp":"DISABLED"}}}]}'
        )
        commands.run.return_value = MagicMock(returncode=0, stdout=describe_json)

        with (
            patch.object(runner, "stop_cluster_tasks") as mock_stop,
            patch.object(runner, "run_task", return_value="new-arn") as mock_run,
        ):
            arn = runner.restart_service_task(cluster="c", service="s")

        mock_stop.assert_called_once_with("c")
        mock_run.assert_called_once_with(
            cluster="c",
            task_definition="td-arn",
            subnets=["sub-1"],
            security_groups=["sg-1"],
        )
        assert arn == "new-arn"

    def test_refresh_propagates_wait_ready_failure(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        localstack = MagicMock(spec=LocalStack)
        localstack.wait_ready.side_effect = RunnerError("localstack down")
        runner = build_runner(commands, localstack)

        with pytest.raises(RunnerError, match="localstack down"):
            runner.refresh()

        commands.run.assert_not_called()
