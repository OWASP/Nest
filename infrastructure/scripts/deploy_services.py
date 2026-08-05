"""Deploy backend and frontend ECS services on LocalStack."""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

from botocore.exceptions import ClientError

from scripts.aws import aws_client
from scripts.commands import CommandRunner
from scripts.errors import InfrastructureError
from scripts.localstack import LocalStack

logger = logging.getLogger(__name__)

TFLOCAL = "tflocal"
DOCKER = "docker"
STACK_PREFIX = "nest-local"
SSM_PARAM_TYPE = "String"
BACKEND_PORT = 8000
FRONTEND_PORT = 3000
TASK_WAIT_ATTEMPTS = 30
TASK_WAIT_INTERVAL = 5
HEALTH_MAX_ATTEMPTS = 36
HEALTH_POLL_INTERVAL = 10


class DeployServices:
    """Run backend/frontend ECS tasks on LocalStack and register ALB targets."""

    def __init__(
        self,
        commands: CommandRunner | None = None,
        *,
        localstack: LocalStack | None = None,
    ) -> None:
        """Initialize the service deployer.

        Args:
            commands (CommandRunner, optional): Command runner instance.
            localstack (LocalStack, optional): LocalStack manager instance.

        """
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.infra_dir = self.root_dir / "infrastructure"
        self.live_dir = self.infra_dir / "live"
        self.commands = commands or CommandRunner()
        self.localstack = localstack or LocalStack(self.commands)

    @property
    def prefix(self) -> str:
        """Return the SSM parameter prefix for the current environment."""
        return f"/nest/{os.environ.get('ENVIRONMENT', 'local')}"

    def run(self) -> None:
        """Deploy the backend and frontend services on LocalStack.

        Raises:
            CommandNotFoundError: If a required executable is missing.
            InfrastructureError: If deploying the services fails.

        """
        self.commands.require(TFLOCAL)
        self.commands.require(DOCKER)

        logger.info("Deploying ECS services...")
        outputs = self._terraform_outputs()
        self._set_runtime_parameters()

        backend_task = self._deploy_service(
            cluster=outputs["backend_cluster_name"],
            sg_name=f"{STACK_PREFIX}-backend-sg",
            tg_arn=outputs["backend_target_group_arn"],
            task_definition=f"{STACK_PREFIX}-backend",
            port=BACKEND_PORT,
            subnets=outputs["tasks_subnet_ids"],
            service_name="Backend",
        )
        frontend_task = self._deploy_service(
            cluster=outputs["frontend_cluster_name"],
            sg_name=f"{STACK_PREFIX}-frontend-sg",
            tg_arn=outputs["frontend_target_group_arn"],
            task_definition=f"{STACK_PREFIX}-frontend",
            port=FRONTEND_PORT,
            subnets=outputs["tasks_subnet_ids"],
            service_name="Frontend",
        )

        self._check_health(outputs["backend_target_group_arn"], "Backend")
        self._check_health(outputs["frontend_target_group_arn"], "Frontend")
        self._log_summary(outputs["alb_dns_name"], backend_task, frontend_task)

    def _terraform_outputs(self) -> dict:
        """Return the Terraform outputs as a dict.

        Returns:
            dict: A mapping of output name to its value.

        Raises:
            InfrastructureError: If the outputs cannot be fetched or parsed.

        """
        result = self.commands.run(
            TFLOCAL,
            "output",
            "-json",
            cwd=self.live_dir,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            message = "Failed to get Terraform outputs. Run 'make provision-infra' first."
            raise InfrastructureError(message)
        try:
            raw = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            message = "Failed to parse 'tflocal output -json'."
            raise InfrastructureError(message) from exc
        return {name: entry["value"] for name, entry in raw.items()}

    def _set_runtime_parameters(self) -> None:
        """Overwrite SSM parameters with the actual LocalStack host and ports.

        LocalStack assigns its own ports for Elasticache and RDS, so the runtime
        parameters must reflect the discovered values instead of the configured
        ones.
        """
        container_ip = self._container_ip()
        redis_port = self._redis_port()
        db_port = self._db_port()

        logger.info("  Setting DJANGO_REDIS_HOST to LocalStack container IP: %s", container_ip)
        self._put_ssm(f"{self.prefix}/DJANGO_REDIS_HOST", container_ip)
        logger.info("  Setting DJANGO_REDIS_PORT to actual Elasticache port: %d", redis_port)
        self._put_ssm(f"{self.prefix}/DJANGO_REDIS_PORT", str(redis_port))
        logger.info("  Setting DJANGO_DB_HOST to LocalStack container IP: %s", container_ip)
        self._put_ssm(f"{self.prefix}/DJANGO_DB_HOST", container_ip)
        logger.info("  Setting DJANGO_DB_PORT to actual RDS port: %d", db_port)
        self._put_ssm(f"{self.prefix}/DJANGO_DB_PORT", str(db_port))

    def _container_ip(self) -> str:
        """Return the bridge IP address of the LocalStack container.

        Returns:
            str: The container's bridge IP address.

        """
        result = self.commands.run(
            DOCKER,
            "inspect",
            self.localstack.container_name,
            "--format",
            "{{.NetworkSettings.Networks.bridge.IPAddress}}",
            capture_output=True,
            check=True,
        )
        return result.stdout.strip()

    def _redis_port(self) -> int:
        """Return the actual Redis port assigned by LocalStack.

        Returns:
            int: The discovered Elasticache primary endpoint port.

        """
        elasticache = aws_client("elasticache", localstack=self.localstack)
        response = elasticache.describe_replication_groups(
            ReplicationGroupId=f"{STACK_PREFIX}-cache"
        )
        return int(response["ReplicationGroups"][0]["NodeGroups"][0]["PrimaryEndpoint"]["Port"])

    def _db_port(self) -> int:
        """Return the actual RDS port assigned by LocalStack.

        Returns:
            int: The discovered database instance endpoint port.

        """
        rds = aws_client("rds", localstack=self.localstack)
        response = rds.describe_db_instances(DBInstanceIdentifier=f"{STACK_PREFIX}-db")
        return int(response["DBInstances"][0]["Endpoint"]["Port"])

    def _put_ssm(self, name: str, value: str) -> None:
        """Put an SSM parameter, overwriting any existing value.

        Args:
            name (str): The parameter name.
            value (str): The parameter value.

        """
        ssm = aws_client("ssm", localstack=self.localstack)
        ssm.put_parameter(Name=name, Value=value, Type=SSM_PARAM_TYPE, Overwrite=True)

    def _security_group_id(self, name: str) -> str:
        """Return the security group ID for a group name.

        Args:
            name (str): The security group name.

        Returns:
            str: The security group ID.

        """
        ec2 = aws_client("ec2", localstack=self.localstack)
        response = ec2.describe_security_groups(Filters=[{"Name": "group-name", "Values": [name]}])
        return response["SecurityGroups"][0]["GroupId"]

    def _run_task(
        self,
        cluster: str,
        sg_id: str,
        task_definition: str,
        subnets: list[str],
    ) -> str:
        """Start a Fargate task on LocalStack.

        Args:
            cluster (str): The ECS cluster name.
            sg_id (str): The security group ID.
            task_definition (str): The ECS task definition family.
            subnets (list[str]): The subnets for the task.

        Returns:
            str: The ARN of the started task.

        """
        ecs = aws_client("ecs", localstack=self.localstack)
        response = ecs.run_task(
            cluster=cluster,
            launchType="FARGATE",
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": subnets,
                    "securityGroups": [sg_id],
                    "assignPublicIp": "ENABLED",
                }
            },
            taskDefinition=task_definition,
        )
        return response["tasks"][0]["taskArn"]

    def _wait_for_task_running(self, cluster: str, task_arn: str, service_name: str) -> None:
        """Block until an ECS task is RUNNING.

        Args:
            cluster (str): The ECS cluster name.
            task_arn (str): The task ARN.
            service_name (str): The human-readable service name for logs.

        Raises:
            InfrastructureError: If the task stops or does not become RUNNING.

        """
        ecs = aws_client("ecs", localstack=self.localstack)
        logger.info("  Waiting for %s task to be RUNNING...", service_name)
        for _ in range(TASK_WAIT_ATTEMPTS):
            response = ecs.describe_tasks(cluster=cluster, tasks=[task_arn])
            status = response["tasks"][0]["lastStatus"]
            if status == "RUNNING":
                logger.info("  %s task is RUNNING.", service_name)
                return
            if status == "STOPPED":
                reason = response["tasks"][0].get("stoppedReason", "unknown")
                message = f"{service_name} task STOPPED: {reason}"
                raise InfrastructureError(message)
            time.sleep(TASK_WAIT_INTERVAL)
        timeout = TASK_WAIT_ATTEMPTS * TASK_WAIT_INTERVAL
        message = f"{service_name} task did not become RUNNING after {timeout} seconds."
        raise InfrastructureError(message)

    def _task_docker_ip(self, task_arn: str) -> str:
        """Return the Docker bridge IP address of an ECS task container.

        Args:
            task_arn (str): The task ARN.

        Returns:
            str: The container's bridge IP address.

        Raises:
            InfrastructureError: If no Docker container matches the task.

        """
        task_id = task_arn.rsplit("/", 1)[-1]
        result = self.commands.run(
            DOCKER,
            "ps",
            "--format",
            "{{.Names}}",
            capture_output=True,
            check=True,
        )
        container = next(
            (name for name in result.stdout.splitlines() if task_id in name),
            None,
        )
        if container is None:
            message = f"Could not find Docker container for task {task_id}"
            raise InfrastructureError(message)
        inspect = self.commands.run(
            DOCKER,
            "inspect",
            container,
            "--format",
            "{{.NetworkSettings.Networks.bridge.IPAddress}}",
            capture_output=True,
            check=True,
        )
        return inspect.stdout.strip()

    def _register_target(self, tg_arn: str, ip: str, port: int) -> None:
        """Register an IP target with an ALB target group.

        Args:
            tg_arn (str): The target group ARN.
            ip (str): The target IP address.
            port (int): The target port.

        """
        elbv2 = aws_client("elbv2", localstack=self.localstack)
        elbv2.register_targets(TargetGroupArn=tg_arn, Targets=[{"Id": ip, "Port": port}])

    def _check_health(self, tg_arn: str, service_name: str) -> None:
        """Wait until a target group reports a healthy target.

        Args:
            tg_arn (str): The target group ARN.
            service_name (str): The human-readable service name for logs.

        Raises:
            InfrastructureError: If the target does not become healthy.

        """
        elbv2 = aws_client("elbv2", localstack=self.localstack)
        for attempt in range(1, HEALTH_MAX_ATTEMPTS + 1):
            try:
                response = elbv2.describe_target_health(TargetGroupArn=tg_arn)
                health = response["TargetHealthDescriptions"][0]["TargetHealth"]["State"]
            except ClientError:
                health = "unknown"
            if health == "healthy":
                logger.info("  %s target group health: healthy", service_name)
                return
            logger.info(
                "  %s target group: %s (attempt %s/%s)",
                service_name,
                health,
                attempt,
                HEALTH_MAX_ATTEMPTS,
            )
            time.sleep(HEALTH_POLL_INTERVAL)
        message = f"{service_name} target did not become healthy."
        raise InfrastructureError(message)

    def _deploy_service(
        self,
        *,
        cluster: str,
        sg_name: str,
        tg_arn: str,
        task_definition: str,
        port: int,
        subnets: list[str],
        service_name: str,
    ) -> str:
        """Run a service's ECS task and register its ALB target.

        Args:
            cluster (str): The ECS cluster name.
            sg_name (str): The security group name.
            tg_arn (str): The target group ARN.
            task_definition (str): The ECS task definition family.
            port (int): The container port to register with the target group.
            subnets (list[str]): The subnets for the Fargate task.
            service_name (str): The human-readable service name for logs.

        Returns:
            str: The ARN of the started ECS task.

        """
        logger.info("")
        logger.info("--- %s ---", service_name)
        sg_id = self._security_group_id(sg_name)
        logger.info("  Cluster: %s", cluster)
        logger.info("  Security Group: %s", sg_id)
        logger.info("  Target Group ARN: %s", tg_arn)

        task_arn = self._run_task(cluster, sg_id, task_definition, subnets)
        logger.info("  Task ARN: %s", task_arn)

        self._wait_for_task_running(cluster, task_arn, service_name)

        ip = self._task_docker_ip(task_arn)
        logger.info("  %s Docker bridge IP: %s", service_name, ip)

        logger.info("  Registering %s target with ALB...", service_name.lower())
        self._register_target(tg_arn, ip, port)
        return task_arn

    def _log_summary(self, alb_dns: str, backend_task: str, frontend_task: str) -> None:
        """Log a summary of the deployment.

        Args:
            alb_dns (str): The ALB DNS name.
            backend_task (str): The backend task ARN.
            frontend_task (str): The frontend task ARN.

        """
        logger.info("")
        logger.info("--- Deployment Complete ---")
        logger.info("  ALB DNS: %s", alb_dns)
        logger.info("  Backend: https://%s/status/", alb_dns)
        logger.info("  Frontend: https://%s/", alb_dns)
        logger.info("")
        logger.info("  Backend task: %s", backend_task)
        logger.info("  Frontend task: %s", frontend_task)
