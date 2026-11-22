"""Tests for ``scripts.backend_tasks_runner``."""

import logging
import os
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from scripts.backend_tasks_runner import (
    POLL_INTERVAL_SECONDS,
    BackendTaskRunner,
)
from scripts.commands import CommandRunner
from scripts.errors import RunnerError
from scripts.localstack import LocalStack

LOCALSTACK_ENDPOINT_URL = "http://localhost:4566"  # NOSONAR: Test-only LocalStack HTTP.
TASK_STOPPED = {"lastStatus": "STOPPED"}


def build_runner(commands: MagicMock) -> BackendTaskRunner:
    localstack = MagicMock(spec=LocalStack)
    localstack.api_url = LOCALSTACK_ENDPOINT_URL
    return BackendTaskRunner(
        "migrate",
        commands=commands,
        localstack=localstack,
        root_dir=Path("/repo"),
    )


class TestBackendTaskRunner:
    """Tests for ``BackendTaskRunner`` orchestration."""

    def test_init_rejects_unknown_task_name(self) -> None:
        commands = MagicMock(spec=CommandRunner)

        with pytest.raises(RunnerError, match="unknown backend task: nope"):
            BackendTaskRunner("nope", commands=commands, root_dir=Path("/repo"))

    def test_check_task_result_accepts_zero_exit_code(self) -> None:
        runner = build_runner(MagicMock(spec=CommandRunner))

        runner.check_task_result({"containers": [{"exitCode": 0}]})

    def test_check_task_result_raises_on_non_zero_exit_code(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        commands = MagicMock(spec=CommandRunner)
        runner = build_runner(commands)
        task = {
            "containers": [{"exitCode": 3}],
            "stoppedReason": "Essential container exited",
        }

        with (
            patch.object(runner, "fetch_task_logs", return_value=["line-1"]) as mock_logs,
            caplog.at_level(logging.ERROR),
            pytest.raises(RunnerError, match=r"failed \(exit code 3\)"),
        ):
            runner.check_task_result(task)

        mock_logs.assert_called_once_with()
        assert "line-1" in caplog.text

    def test_check_task_result_warns_when_exit_code_is_missing(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        runner = build_runner(MagicMock(spec=CommandRunner))

        with caplog.at_level(logging.WARNING):
            runner.check_task_result({"containers": [{}]})

        assert "without reporting an exit code" in caplog.text

    def test_describe_task_returns_first_task(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(
            returncode=0, stdout='{"tasks": [{"lastStatus": "RUNNING"}]}'
        )
        runner = build_runner(commands)

        task = runner.describe_task("cluster-1", "arn-1")

        assert task == {"lastStatus": "RUNNING"}
        commands.run.assert_called_once_with(
            "awslocal",
            "ecs",
            "describe-tasks",
            "--cluster",
            "cluster-1",
            "--tasks",
            "arn-1",
            "--output",
            "json",
            capture_output=True,
        )

    def test_describe_task_raises_when_command_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=1, stderr="boom")
        runner = build_runner(commands)

        with pytest.raises(RunnerError, match="awslocal ecs describe-tasks failed"):
            runner.describe_task("cluster-1", "arn-1")

    def test_describe_task_raises_when_no_task_is_found(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=0, stdout='{"tasks": []}')
        runner = build_runner(commands)

        with pytest.raises(RunnerError, match="no task found for arn-1"):
            runner.describe_task("cluster-1", "arn-1")

    def test_fetch_task_logs_returns_latest_messages(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [
            MagicMock(
                returncode=0,
                stdout='{"logStreams": [{"logStreamName": "stream-1"}]}',
            ),
            MagicMock(
                returncode=0,
                stdout='{"events": [{"message": "m-1"}, {"message": "m-2"}]}',
            ),
        ]
        runner = build_runner(commands)

        assert runner.fetch_task_logs() == ["m-1", "m-2"]

    def test_fetch_task_logs_returns_empty_on_failure(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=1, stderr="no logs")
        runner = build_runner(commands)

        assert runner.fetch_task_logs() == []

    def test_launch_task_runs_task_with_network_configuration(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(
            returncode=0, stdout='{"tasks": [{"taskArn": "arn-1"}]}'
        )
        runner = build_runner(commands)

        with patch("scripts.backend_tasks_runner.read_live_output") as mock_output:
            mock_output.side_effect = ["sg-1", ["subnet-1", "subnet-2"]]

            task_arn = runner.launch_task("cluster-1")

        assert task_arn == "arn-1"
        live_dir = Path("/repo") / "infrastructure" / "live"
        mock_output.assert_has_calls(
            [
                call(commands, live_dir, "tasks_security_group_id"),
                call(commands, live_dir, "tasks_subnet_ids", json_output=True),
            ]
        )
        expected_network = (
            "awsvpcConfiguration={"
            "subnets=[subnet-1,subnet-2],"
            "securityGroups=[sg-1],"
            "assignPublicIp=DISABLED}"
        )
        commands.run.assert_called_once_with(
            "awslocal",
            "ecs",
            "run-task",
            "--cluster",
            "cluster-1",
            "--launch-type",
            "FARGATE",
            "--network-configuration",
            expected_network,
            "--task-definition",
            "nest-production-migrate",
            "--output",
            "json",
            capture_output=True,
        )

    def test_launch_task_raises_when_run_task_fails(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=1, stderr="boom")
        runner = build_runner(commands)

        with (
            patch(
                "scripts.backend_tasks_runner.read_live_output",
                return_value="sg-1",
            ),
            pytest.raises(RunnerError, match="awslocal ecs run-task failed"),
        ):
            runner.launch_task("cluster-1")

    def test_launch_task_raises_when_no_task_is_returned(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=0, stdout='{"tasks": []}')
        runner = build_runner(commands)

        with (
            patch(
                "scripts.backend_tasks_runner.read_live_output",
                return_value="sg-1",
            ),
            pytest.raises(RunnerError, match="returned no tasks"),
        ):
            runner.launch_task("cluster-1")

    @patch.dict(os.environ, {}, clear=True)
    def test_run_initializes_terraform_then_launches_waits_and_checks(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        runner = build_runner(commands)
        task = {"lastStatus": "STOPPED", "containers": [{"exitCode": 0}]}
        live_dir = Path("/repo") / "infrastructure" / "live"
        call_order: list[str] = []
        captured: dict[str, str] = {}

        def record_init(*_args, **_kwargs) -> None:
            call_order.append("init_live_configuration")
            captured["init_aws_access_key_id"] = os.environ["AWS_ACCESS_KEY_ID"]

        def record_read_output(*_args, **_kwargs) -> str:
            call_order.append("read_live_output")
            captured["read_aws_endpoint_url"] = os.environ["AWS_ENDPOINT_URL"]
            return "cluster-1"

        with (
            patch(
                "scripts.backend_tasks_runner.init_live_configuration",
                side_effect=record_init,
            ) as mock_init,
            patch(
                "scripts.backend_tasks_runner.read_live_output",
                side_effect=record_read_output,
            ) as mock_read,
            patch.object(runner, "launch_task", return_value="arn-1") as mock_launch,
            patch.object(runner, "wait_for_task", return_value=task) as mock_wait,
            patch.object(runner, "check_task_result") as mock_check,
        ):
            runner.run()

        assert call_order == ["init_live_configuration", "read_live_output"]
        assert captured["init_aws_access_key_id"] == "test"
        assert captured["read_aws_endpoint_url"] == LOCALSTACK_ENDPOINT_URL
        assert "AWS_ACCESS_KEY_ID" not in os.environ
        assert "AWS_ENDPOINT_URL" not in os.environ
        assert "AWS_SECRET_ACCESS_KEY" not in os.environ
        mock_init.assert_called_once_with(commands, live_dir, "terraform.localstack.tfbackend")
        mock_read.assert_any_call(commands, live_dir, "tasks_cluster_name")
        mock_launch.assert_called_once_with("cluster-1")
        mock_wait.assert_called_once_with("cluster-1", "arn-1")
        mock_check.assert_called_once_with(task)

    def test_wait_for_task_returns_final_description_when_stopped(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [
            MagicMock(returncode=0, stdout='{"tasks": [{"lastStatus": "RUNNING"}]}'),
            MagicMock(returncode=0, stdout='{"tasks": [{"lastStatus": "STOPPED"}]}'),
        ]
        runner = build_runner(commands)

        with patch("scripts.backend_tasks_runner.time.sleep") as mock_sleep:
            task = runner.wait_for_task("cluster-1", "arn-1")

        assert task == TASK_STOPPED
        mock_sleep.assert_called_once_with(POLL_INTERVAL_SECONDS)

    def test_wait_for_task_raises_on_timeout(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(
            returncode=0, stdout='{"tasks": [{"lastStatus": "RUNNING"}]}'
        )
        runner = build_runner(commands)

        with (
            patch("scripts.backend_tasks_runner.time.sleep"),
            pytest.raises(RunnerError, match="did not stop within"),
        ):
            runner.wait_for_task("cluster-1", "arn-1")
