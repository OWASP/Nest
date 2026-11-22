"""Backend ECS task orchestration."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from scripts.commands import CommandRunner
from scripts.constants import LIVE_DIR, LOCALSTACK_TFBACKEND
from scripts.errors import RunnerError
from scripts.localstack import LocalStack
from scripts.utils import init_live_configuration, localstack_aws_env, read_live_output

logger = logging.getLogger(__name__)

BACKEND_TASKS = ("index-data", "load-data", "migrate")
LOG_GROUP_PREFIX = "/aws/ecs"
LOG_TAIL_EVENTS = 30
POLL_INTERVAL_SECONDS = 10
POLL_MAX_ATTEMPTS = 120
TASK_DEFINITION_PREFIX = "nest-production"
TASK_STATUS_STOPPED = "STOPPED"


class BackendTaskRunner:
    """ECS backend task launcher."""

    def __init__(
        self,
        task_name: str,
        *,
        commands: CommandRunner | None = None,
        localstack: LocalStack | None = None,
        root_dir: Path | None = None,
    ) -> None:
        """Initialize the ECS backend task launcher.

        Args:
            task_name (str): The backend task name.
            commands (CommandRunner, optional): Command runner instance.
            localstack (LocalStack, optional): LocalStack container manager.
            root_dir (Path, optional): The repository root directory.

        Raises:
            RunnerError: If the task name is not a known backend task.

        """
        if task_name not in BACKEND_TASKS:
            message = f"unknown backend task: {task_name}"
            raise RunnerError(message)
        self.commands = commands or CommandRunner()
        self.localstack = localstack or LocalStack(self.commands)
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent.parent
        self.task_name = task_name

    def check_task_result(self, task: dict) -> None:
        """Verify that the backend task completed successfully.

        Args:
            task (dict): The final task description.

        Raises:
            RunnerError: If the task container exited with a non-zero code.

        """
        containers = task.get("containers", [])
        exit_code = containers[0].get("exitCode") if containers else None
        if exit_code is None:
            logger.warning("Task stopped without reporting an exit code.")
            return
        if str(exit_code) != "0":
            logger.error(
                "Task failed (exit %s): %s",
                exit_code,
                task.get("stoppedReason", ""),
            )
            for line in self.fetch_task_logs():
                logger.error(line)
            message = f"{self.task_definition} failed (exit code {exit_code})."
            raise RunnerError(message)

    def describe_task(self, cluster: str, task_arn: str) -> dict:
        """Fetch the current description of a task.

        Args:
            cluster (str): The ECS cluster name.
            task_arn (str): The ARN of the task.

        Returns:
            dict: The task description.

        Raises:
            RunnerError: If awslocal ecs describe-tasks fails or returns no task.

        """
        result = self.commands.run(
            "awslocal",
            "ecs",
            "describe-tasks",
            "--cluster",
            cluster,
            "--tasks",
            task_arn,
            "--output",
            "json",
            capture_output=True,
        )
        if result.returncode != 0:
            message = f"awslocal ecs describe-tasks failed: {result.stderr}"
            raise RunnerError(message)
        tasks = json.loads(result.stdout).get("tasks", [])
        if not tasks:
            message = f"no task found for {task_arn}"
            raise RunnerError(message)
        return tasks[0]

    def fetch_task_logs(self) -> list[str]:
        """Fetch the most recent log events from the task's log group.

        Returns:
            list[str]: The latest log messages, empty if unavailable.

        """
        log_group = f"{LOG_GROUP_PREFIX}/{self.task_definition}"
        try:
            streams_result = self.commands.run(
                "awslocal",
                "logs",
                "describe-log-streams",
                "--log-group-name",
                log_group,
                "--order-by",
                "LastEventTime",
                "--descending",
                "--limit",
                "1",
                "--output",
                "json",
                capture_output=True,
                check=False,
            )
            if streams_result.returncode != 0:
                return []
            streams = json.loads(streams_result.stdout).get("logStreams", [])
            if not streams:
                return []
            events_result = self.commands.run(
                "awslocal",
                "logs",
                "get-log-events",
                "--log-group-name",
                log_group,
                "--log-stream-name",
                streams[0]["logStreamName"],
                "--output",
                "json",
                capture_output=True,
                check=False,
            )
            if events_result.returncode != 0:
                return []
            events = json.loads(events_result.stdout).get("events", [])
            return [event["message"] for event in events][-LOG_TAIL_EVENTS:]
        except (KeyError, TypeError, ValueError):
            return []

    def launch_task(self, cluster: str) -> str:
        """Run the task definition on the cluster and return the task ARN.

        Args:
            cluster (str): The ECS cluster name.

        Returns:
            str: The ARN of the launched task.

        Raises:
            RunnerError: If awslocal ecs run-task fails or returns no task.

        """
        security_group = read_live_output(self.commands, self.live_dir, "tasks_security_group_id")
        subnets = read_live_output(
            self.commands, self.live_dir, "tasks_subnet_ids", json_output=True
        )
        network_configuration = (
            "awsvpcConfiguration={"
            f"subnets=[{','.join(subnets)}],"
            f"securityGroups=[{security_group}],"
            "assignPublicIp=DISABLED}"
        )
        result = self.commands.run(
            "awslocal",
            "ecs",
            "run-task",
            "--cluster",
            cluster,
            "--launch-type",
            "FARGATE",
            "--network-configuration",
            network_configuration,
            "--task-definition",
            self.task_definition,
            "--output",
            "json",
            capture_output=True,
        )
        if result.returncode != 0:
            message = f"awslocal ecs run-task failed: {result.stderr}"
            raise RunnerError(message)
        tasks = json.loads(result.stdout).get("tasks", [])
        if not tasks:
            message = f"awslocal ecs run-task returned no tasks for {self.task_name}"
            raise RunnerError(message)
        task_arn = tasks[0]["taskArn"]
        logger.info("Launched task %s (%s).", self.task_definition, task_arn)
        return task_arn

    def run(self) -> None:
        """Launch the backend task and wait for it to complete.

        Raises:
            RunnerError: If the task fails to launch or exits with an error.

        """
        with localstack_aws_env(self.localstack.api_url):
            init_live_configuration(self.commands, self.live_dir, LOCALSTACK_TFBACKEND)
            cluster = read_live_output(self.commands, self.live_dir, "tasks_cluster_name")
            task_arn = self.launch_task(cluster)
        task = self.wait_for_task(cluster, task_arn)
        self.check_task_result(task)
        logger.info("Backend task %s completed successfully.", self.task_name)

    @property
    def live_dir(self) -> Path:
        """Return the live/ Terraform configuration directory."""
        return self.root_dir / LIVE_DIR

    @property
    def task_definition(self) -> str:
        """Return the task definition family for the backend task."""
        return f"{TASK_DEFINITION_PREFIX}-{self.task_name}"

    def wait_for_task(self, cluster: str, task_arn: str) -> dict:
        """Block until the task stops and return its final description.

        Args:
            cluster (str): The ECS cluster name.
            task_arn (str): The ARN of the task to wait for.

        Returns:
            dict: The final task description.

        Raises:
            RunnerError: If the task does not stop within the timeout.

        """
        for attempt in range(1, POLL_MAX_ATTEMPTS + 1):
            task = self.describe_task(cluster, task_arn)
            status = task.get("lastStatus")
            if status == TASK_STATUS_STOPPED:
                return task
            logger.info(
                "Waiting for task... (attempt %s/%s, status %s)",
                attempt,
                POLL_MAX_ATTEMPTS,
                status,
            )
            if attempt == POLL_MAX_ATTEMPTS:
                timeout = POLL_MAX_ATTEMPTS * POLL_INTERVAL_SECONDS
                message = f"task {task_arn} did not stop within {timeout} seconds."
                raise RunnerError(message)
            time.sleep(POLL_INTERVAL_SECONDS)
        message = f"task {task_arn} did not stop."
        raise RunnerError(message)
