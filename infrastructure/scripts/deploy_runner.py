"""Infrastructure deployment orchestration."""

import json
import logging
import time
from pathlib import Path

from scripts.commands import CommandRunner
from scripts.constants import LIVE_DIR, STATE_DIR
from scripts.errors import RunnerError
from scripts.images import IMAGE_CONFIG, ImageManager
from scripts.localstack import LocalStack
from scripts.utils import (
    chdir_repository_root,
    configure_terraform_cache,
    set_temporary_env,
)

logger = logging.getLogger(__name__)

LOCALSTACK_TFBACKEND = "terraform.localstack.tfbackend"
LOCALSTACK_TFVARS = "terraform.localstack.tfvars"


class InfrastructureDeployRunner:
    """Infrastructure deployment orchestrator."""

    def __init__(
        self,
        root_dir: Path | None = None,
        *,
        commands: CommandRunner | None = None,
        images: ImageManager | None = None,
        localstack: LocalStack | None = None,
    ) -> None:
        """Initialize the infrastructure deployment orchestrator.

        Args:
            root_dir (Path, optional): The root directory of the project.
            commands (CommandRunner, optional): Command runner instance.
            images (ImageManager, optional): ECR image manager instance.
            localstack (LocalStack, optional): LocalStack manager instance.

        """
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent.parent
        self.commands = commands or CommandRunner()
        self.localstack = localstack or LocalStack(self.commands)
        self.images = images or ImageManager(
            self.root_dir,
            commands=self.commands,
            localstack=self.localstack,
        )

    def apply_live(
        self,
        *,
        refresh: bool = True,
        var_overrides: dict[str, str] | None = None,
    ) -> None:
        """Initialize and apply the live/ Terraform configuration.

        Args:
            refresh (bool): Whether Terraform should refresh state from the
                real infrastructure before planning. Defaults to True.
            var_overrides (dict[str, str], optional): Terraform variable
                values that take precedence over the tfvars file.

        Raises:
            RunnerError: If a Terraform command exits with a non-zero status.

        """
        self.init_live()
        live_dir = self.root_dir / LIVE_DIR
        apply_args = [
            "tflocal",
            f"-chdir={live_dir}",
            "apply",
            "-auto-approve",
            "-input=false",
            f"-var-file={LOCALSTACK_TFVARS}",
        ]
        for key, value in (var_overrides or {}).items():
            apply_args += ["-var", f"{key}={value}"]
        if not refresh:
            apply_args.append("-refresh=false")

        apply_result = self.commands.run(
            *apply_args,
            check=False,
        )
        if apply_result.returncode != 0:
            message = f"terraform apply failed in {live_dir}"
            raise RunnerError(message)

    def apply_state(self) -> None:
        """Initialize and apply the state/ Terraform configuration.

        Raises:
            RunnerError: If a Terraform command exits with a non-zero status.

        """
        state_dir = self.root_dir / STATE_DIR
        init_result = self.commands.run(
            "tflocal",
            f"-chdir={state_dir}",
            "init",
            "-input=false",
            "-reconfigure",
            check=False,
        )
        if init_result.returncode != 0:
            message = f"terraform init failed in {state_dir}"
            raise RunnerError(message)

        apply_result = self.commands.run(
            "tflocal",
            f"-chdir={state_dir}",
            "apply",
            "-auto-approve",
            "-input=false",
            f"-var-file={LOCALSTACK_TFVARS}",
            check=False,
        )
        if apply_result.returncode != 0:
            message = f"terraform apply failed in {state_dir}"
            raise RunnerError(message)

    def configure_environment(self) -> None:
        """Change to the repo root and configure the Terraform plugin cache."""
        chdir_repository_root(self.root_dir)
        try:
            configure_terraform_cache()
        except OSError as exc:
            logger.warning("Could not configure TF_PLUGIN_CACHE_DIR: %s", exc)

    def deploy(self) -> None:
        """Orchestrate a deployment.

        Raises:
            RunnerError: If a Terraform command exits with a non-zero status.

        """
        self.commands.require("tflocal")
        self.localstack.wait_ready()

        with (
            set_temporary_env("AWS_ACCESS_KEY_ID", "test"),
            set_temporary_env("AWS_ENDPOINT_URL", self.localstack.api_url),
            set_temporary_env("AWS_SECRET_ACCESS_KEY", "test"),
        ):
            self.apply_state()
            self.apply_live()
        logger.info("Deployment on LocalStack successful!")

    def init_live(self) -> None:
        """Initialize Terraform for the live/ configuration.

        Raises:
            RunnerError: If terraform init exits with a non-zero status.

        """
        live_dir = self.root_dir / LIVE_DIR
        result = self.commands.run(
            "tflocal",
            f"-chdir={live_dir}",
            "init",
            f"-backend-config={LOCALSTACK_TFBACKEND}",
            "-input=false",
            "-reconfigure",
            check=False,
        )
        if result.returncode != 0:
            message = f"terraform init failed in {live_dir}"
            raise RunnerError(message)

    def push_images(self) -> dict[str, str]:
        """Build and push all service images to ECR.

        Returns:
            dict[str, str]: Mapping of service name to the pushed image tag.

        """
        self.images.login()
        tag = str(int(time.time()))
        for service in IMAGE_CONFIG:
            self.images.build(service, tag)
            self.images.push(service, tag)
        return dict.fromkeys(IMAGE_CONFIG, tag)

    def refresh(self) -> None:
        """Orchestrate a deployment refresh.

        Raises:
            RunnerError: If a Terraform command exits with a non-zero status.

        """
        self.commands.require("tflocal")
        self.localstack.wait_ready()

        with (
            set_temporary_env("AWS_ACCESS_KEY_ID", "test"),
            set_temporary_env("AWS_ENDPOINT_URL", self.localstack.api_url),
            set_temporary_env("AWS_SECRET_ACCESS_KEY", "test"),
        ):
            self.init_live()
            tags = self.push_images()
            # TODO(rudransh-shrivastava): LocalStack updates port mappings,
            # computed endpoints, and more to its preferred configuration after terraform apply.
            # use -refresh=false to prevent updating them back.
            # Ideal fix is to pass LocalStack preferred configuration via tfvars.
            self.apply_live(
                refresh=False,
                var_overrides={f"{svc}_image_tag": tag for svc, tag in tags.items()},
            )
            # LocalStack's ECS scheduler does not spawn tasks after service updates.
            # Stop existing tasks and run new tasks.
            for service in IMAGE_CONFIG:
                self.restart_service_task(
                    cluster=f"nest-production-{service}-cluster",
                    service=f"nest-production-{service}-service",
                )
        logger.info("Deployment on LocalStack successful!")

    def restart_service_task(self, *, cluster: str, service: str) -> str:
        """Stop existing tasks in a cluster and start a fresh task for a service.

        Args:
            cluster (str): The ECS cluster hosting the service.
            service (str): The ECS service name.

        Returns:
            str: The ARN of the newly started task.

        Raises:
            RunnerError: If any awslocal command fails.

        """
        self.commands.require("awslocal")
        self.stop_cluster_tasks(cluster)
        result = self.commands.run(
            "awslocal",
            "ecs",
            "describe-services",
            "--cluster",
            cluster,
            "--services",
            service,
            capture_output=True,
        )
        if result.returncode != 0:
            message = f"awslocal ecs describe-services failed: {result.stderr}"
            raise RunnerError(message)

        service_data = json.loads(result.stdout)["services"][0]
        network = service_data["networkConfiguration"]["awsvpcConfiguration"]
        return self.run_task(
            cluster=cluster,
            task_definition=service_data["taskDefinition"],
            subnets=network["subnets"],
            security_groups=network["securityGroups"],
        )

    def run_task(
        self,
        *,
        cluster: str,
        task_definition: str,
        subnets: list[str],
        security_groups: list[str],
    ) -> str:
        """Start a single ECS task and return its ARN.

        Args:
            cluster (str): The ECS cluster name or ARN.
            task_definition (str): The task definition family or ARN.
            subnets (list[str]): Subnet IDs for the task network configuration.
            security_groups (list[str]): Security group IDs for the task network configuration.

        Returns:
            str: The ARN of the started task.

        Raises:
            RunnerError: If awslocal ecs run-task fails.

        """
        self.commands.require("awslocal")
        network = (
            "awsvpcConfiguration={"
            f"subnets=[{','.join(subnets)}],"
            f"securityGroups=[{','.join(security_groups)}],"
            "assignPublicIp=ENABLED"
            "}"
        )
        result = self.commands.run(
            "awslocal",
            "ecs",
            "run-task",
            "--cluster",
            cluster,
            "--task-definition",
            task_definition,
            "--launch-type",
            "FARGATE",
            "--network-configuration",
            network,
            "--query",
            "tasks[0].taskArn",
            "--output",
            "text",
            capture_output=True,
        )
        if result.returncode != 0:
            message = f"awslocal ecs run-task failed: {result.stderr}"
            raise RunnerError(message)
        return result.stdout.strip()

    def stop_cluster_tasks(self, cluster: str) -> None:
        """Stop all RUNNING tasks in a cluster.

        Args:
            cluster (str): The ECS cluster name or ARN.

        Raises:
            RunnerError: If awslocal ecs list-tasks or stop-task fails.

        """
        self.commands.require("awslocal")
        list_result = self.commands.run(
            "awslocal",
            "ecs",
            "list-tasks",
            "--cluster",
            cluster,
            "--desired-status",
            "RUNNING",
            "--query",
            "taskArns",
            "--output",
            "text",
            capture_output=True,
        )
        if list_result.returncode != 0:
            message = f"awslocal ecs list-tasks failed: {list_result.stderr}"
            raise RunnerError(message)

        for arn in list_result.stdout.split():
            stop_result = self.commands.run(
                "awslocal",
                "ecs",
                "stop-task",
                "--cluster",
                cluster,
                "--task",
                arn,
                capture_output=True,
            )
            if stop_result.returncode != 0:
                message = f"awslocal ecs stop-task failed for {arn}: {stop_result.stderr}"
                raise RunnerError(message)
