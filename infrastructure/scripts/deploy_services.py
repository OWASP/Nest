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
SSM_PARAM_TYPE = "String"
SERVICE_DESIRED_COUNT = 1
SERVICE_WAIT_ATTEMPTS = 30
SERVICE_WAIT_INTERVAL = 5
HEALTH_MAX_ATTEMPTS = 36
HEALTH_POLL_INTERVAL = 10


class DeployServices:
    """Start the backend/frontend ECS services on LocalStack."""

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
    def project_name(self) -> str:
        """Return the project name for the current environment."""
        return os.environ.get("PROJECT_NAME", "nest")

    @property
    def environment(self) -> str:
        """Return the active environment name."""
        return os.environ.get("ENVIRONMENT", "local")

    @property
    def stack_prefix(self) -> str:
        """Return the resource name prefix for the active environment."""
        return f"{self.project_name}-{self.environment}"

    @property
    def prefix(self) -> str:
        """Return the SSM parameter prefix for the current environment."""
        return f"/{self.project_name}/{self.environment}"

    def run(self) -> None:
        """Start the backend and frontend ECS services on LocalStack.

        LocalStack only starts a service's tasks when it is created or when its
        ``desiredCount`` changes; it ignores ``forceNewDeployment``. ``provision-infra``
        therefore applies the stack with ``desired_count = 0`` so no task fires before
        the images are pushed. This method overwrites the SSM runtime parameters with
        the real host and ports, then scales each service up so LocalStack starts a
        fresh Fargate task that picks up the corrected configuration. LocalStack
        registers the task with the ALB target group once it is RUNNING.

        Raises:
            CommandNotFoundError: If a required executable is missing.
            InfrastructureError: If deploying the services fails.

        """
        self.commands.require(TFLOCAL)
        self.commands.require(DOCKER)

        logger.info("Deploying ECS services...")
        outputs = self._terraform_outputs()
        self._set_runtime_parameters()

        backend_cluster = outputs["backend_cluster_name"]
        backend_service = outputs["backend_service_name"]
        logger.info("")
        logger.info("--- Backend ---")
        self._start_service(backend_cluster, backend_service, "Backend")
        self._wait_for_service(backend_cluster, backend_service, "Backend")

        frontend_cluster = outputs["frontend_cluster_name"]
        frontend_service = outputs["frontend_service_name"]
        logger.info("")
        logger.info("--- Frontend ---")
        self._start_service(frontend_cluster, frontend_service, "Frontend")
        self._wait_for_service(frontend_cluster, frontend_service, "Frontend")

        self._check_health(outputs["backend_target_group_arn"], "Backend")
        self._check_health(outputs["frontend_target_group_arn"], "Frontend")
        self._log_summary(outputs["alb_dns_name"], backend_service, frontend_service)

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
            ReplicationGroupId=f"{self.stack_prefix}-cache"
        )
        return int(response["ReplicationGroups"][0]["NodeGroups"][0]["PrimaryEndpoint"]["Port"])

    def _db_port(self) -> int:
        """Return the actual RDS port assigned by LocalStack.

        Returns:
            int: The discovered database instance endpoint port.

        """
        rds = aws_client("rds", localstack=self.localstack)
        response = rds.describe_db_instances(DBInstanceIdentifier=f"{self.stack_prefix}-db")
        return int(response["DBInstances"][0]["Endpoint"]["Port"])

    def _put_ssm(self, name: str, value: str) -> None:
        """Put an SSM parameter, overwriting any existing value.

        Args:
            name (str): The parameter name.
            value (str): The parameter value.

        """
        ssm = aws_client("ssm", localstack=self.localstack)
        ssm.put_parameter(Name=name, Value=value, Type=SSM_PARAM_TYPE, Overwrite=True)

    def _start_service(self, cluster: str, service: str, service_name: str) -> None:
        """Scale an ECS service up to its desired task count.

        The service task reads its SSM-backed environment at container start, so
        after ``_set_runtime_parameters`` fixes the placeholder values a fresh
        task is required to pick them up. Scaling down to zero first guarantees a
        replacement task starts: LocalStack's scheduler reacts to ``desiredCount``
        changes but ignores ``forceNewDeployment``.

        Args:
            cluster (str): The ECS cluster name.
            service (str): The ECS service name.
            service_name (str): The human-readable service name for logs.

        """
        ecs = aws_client("ecs", localstack=self.localstack)
        logger.info("  Stopping %s service tasks...", service_name)
        ecs.update_service(cluster=cluster, service=service, desiredCount=0)
        logger.info(
            "  Scaling %s service to %s task(s)...",
            service_name,
            SERVICE_DESIRED_COUNT,
        )
        ecs.update_service(
            cluster=cluster,
            service=service,
            desiredCount=SERVICE_DESIRED_COUNT,
        )

    def _wait_for_service(self, cluster: str, service: str, service_name: str) -> None:
        """Block until an ECS service runs its desired number of tasks.

        Args:
            cluster (str): The ECS cluster name.
            service (str): The ECS service name.
            service_name (str): The human-readable service name for logs.

        Raises:
            InfrastructureError: If the service never reaches its desired count.

        """
        ecs = aws_client("ecs", localstack=self.localstack)
        logger.info("  Waiting for %s service tasks to be RUNNING...", service_name)
        for _ in range(SERVICE_WAIT_ATTEMPTS):
            services = ecs.describe_services(cluster=cluster, services=[service]).get(
                "services", []
            )
            if services and services[0].get("runningCount", 0) >= services[0].get(
                "desiredCount", 0
            ):
                logger.info("  %s service is RUNNING.", service_name)
                return
            time.sleep(SERVICE_WAIT_INTERVAL)
        timeout = SERVICE_WAIT_ATTEMPTS * SERVICE_WAIT_INTERVAL
        message = f"{service_name} service did not reach desired count after {timeout} seconds."
        raise InfrastructureError(message)

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

    def _log_summary(self, alb_dns: str, backend_service: str, frontend_service: str) -> None:
        """Log a summary of the deployment.

        Args:
            alb_dns (str): The ALB DNS name.
            backend_service (str): The backend ECS service name.
            frontend_service (str): The frontend ECS service name.

        """
        logger.info("")
        logger.info("--- Deployment Complete ---")
        logger.info("  ALB DNS: %s", alb_dns)
        logger.info("  Backend: https://%s/status/", alb_dns)
        logger.info("  Frontend: https://%s/", alb_dns)
        logger.info("")
        logger.info("  Backend service: %s", backend_service)
        logger.info("  Frontend service: %s", frontend_service)
