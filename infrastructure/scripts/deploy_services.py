"""Deploy backend and frontend ECS services on LocalStack."""

from __future__ import annotations

import json
import logging
import os
import ssl
import time
from http import HTTPStatus
from http.client import HTTPConnection, HTTPException, HTTPSConnection
from pathlib import Path

from botocore.exceptions import ClientError

from scripts.aws import aws_client
from scripts.commands import CommandRunner
from scripts.errors import InfrastructureError
from scripts.localstack import LOCALSTACK_HTTP_PORT, LOCALSTACK_HTTPS_PORT, LocalStack

logger = logging.getLogger(__name__)

TFLOCAL = "tflocal"
DOCKER = "docker"
SSM_PARAM_TYPE = "String"
SERVICE_DESIRED_COUNT = 1
SERVICE_WAIT_ATTEMPTS = 30
SERVICE_WAIT_INTERVAL = 5
HEALTH_MAX_ATTEMPTS = 36
HEALTH_POLL_INTERVAL = 10
SMOKE_TIMEOUT = 5
SMOKE_MAX_ATTEMPTS = 10
SMOKE_POLL_INTERVAL = 10


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
        self.project_name = "nest"

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
        self._set_url_parameters(outputs["alb_dns_name"])

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
        self._smoke_check(outputs["alb_dns_name"])
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

    @property
    def custom_ports(self) -> bool:
        """Return whether LocalStack publishes non-default HTTP/HTTPS host ports.

        Returns:
            bool: True if either the HTTP or HTTPS host port differs from the
                container default.

        """
        return (
            self.localstack.http_port != LOCALSTACK_HTTP_PORT
            or self.localstack.https_port != LOCALSTACK_HTTPS_PORT
        )

    def _set_url_parameters(self, alb_dns: str) -> None:
        """Overwrite ALB-backed SSM URL parameters with the published host ports.

        Terraform provisions URL parameters with bare hostnames, which only work
        because browsers and Django default to ports 80/443. When LocalStack is
        started with custom host ports (to avoid conflicts), those URLs point at
        ports where nothing listens, so they must be rewritten to include the
        selected ports. Default port usage leaves the provisioned values intact.

        Args:
            alb_dns (str): The ALB DNS name.

        """
        if not self.custom_ports:
            return

        http_port = self.localstack.http_port
        https_port = self.localstack.https_port
        domain = os.environ.get("DOMAIN_NAME", "localhost")
        logger.info(
            "  Setting application URLs to use LocalStack host ports %s (http) and %s (https)...",
            http_port,
            https_port,
        )
        self._put_ssm(f"{self.prefix}/NEXTAUTH_URL", f"http://{alb_dns}:{http_port}/")
        self._put_ssm(
            f"{self.prefix}/NEXT_SERVER_CSRF_URL",
            f"http://{alb_dns}:{http_port}/csrf/",
        )
        self._put_ssm(
            f"{self.prefix}/NEXT_SERVER_GRAPHQL_URL",
            f"http://{alb_dns}:{http_port}/graphql/",
        )
        self._put_ssm(
            f"{self.prefix}/DJANGO_ALLOWED_ORIGINS",
            f"https://{domain}:{https_port},https://{alb_dns}:{https_port}",
        )

    def _app_url(self, alb_dns: str, path: str = "") -> str:
        """Return the externally reachable ALB HTTPS URL for the given path.

        Args:
            alb_dns (str): The ALB DNS name.
            path (str): The URL path to append.

        Returns:
            str: The HTTPS URL including the published host port.

        """
        return f"https://{alb_dns}:{self.localstack.https_port}{path}"

    def _smoke_check(self, alb_dns: str) -> None:
        """Verify the application is reachable through the published host ports.

        Target-group health checks confirm the ECS services are up but never
        exercise the host port mapping. When LocalStack runs on custom ports, a
        request through the published ports is the only way to prove the emitted
        URLs are actually reachable. Skipped entirely when default ports are used.

        Args:
            alb_dns (str): The ALB DNS name.

        Raises:
            InfrastructureError: If any endpoint stays unreachable.

        """
        if not self.custom_ports:
            return

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        checks = (
            ("Frontend", "https", self.localstack.https_port, "/"),
            ("Backend", "https", self.localstack.https_port, "/status/"),
            ("CSRF", "http", self.localstack.http_port, "/csrf/"),
        )
        for attempt in range(1, SMOKE_MAX_ATTEMPTS + 1):
            failures = []
            for name, scheme, port, path in checks:
                connection = self._http_connection(alb_dns, scheme, port, context)
                try:
                    connection.request("GET", path)
                    status = connection.getresponse().status
                    logger.info(
                        "  %s smoke check on %s://%s:%s%s: %s",
                        name,
                        scheme,
                        alb_dns,
                        port,
                        path,
                        status,
                    )
                    if status >= HTTPStatus.BAD_REQUEST:
                        failures.append(f"{name} returned HTTP {status}")
                except (OSError, HTTPException) as exc:
                    failures.append(f"{name} unreachable: {exc}")
                finally:
                    connection.close()

            if not failures:
                return
            if attempt == SMOKE_MAX_ATTEMPTS:
                message = (
                    "Application smoke check failed through published host port"
                    f" {self.localstack.https_port}: {'; '.join(failures)}."
                )
                raise InfrastructureError(message)
            time.sleep(SMOKE_POLL_INTERVAL)

    def _http_connection(self, host: str, scheme: str, port: int, context: ssl.SSLContext):
        """Create an HTTP(S) connection to the given host and port.

        Args:
            host (str): The host to connect to.
            scheme (str): Either "http" or "https".
            port (int): The port to connect to.
            context (ssl.SSLContext): The SSL context to use for HTTPS connections.

        Returns:
            HTTPConnection | HTTPSConnection: The connection object.

        """
        if scheme == "https":
            return HTTPSConnection(host, port, timeout=SMOKE_TIMEOUT, context=context)
        return HTTPConnection(host, port, timeout=SMOKE_TIMEOUT)

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
        task is required to pick them up. Scaling down to zero first and waiting
        for the old task to actually stop guarantees a replacement task starts:
        LocalStack's scheduler reacts to ``desiredCount`` changes but ignores
        ``forceNewDeployment``.

        Args:
            cluster (str): The ECS cluster name.
            service (str): The ECS service name.
            service_name (str): The human-readable service name for logs.

        Raises:
            InfrastructureError: If the service tasks never stop after scaling
                down.

        """
        ecs = aws_client("ecs", localstack=self.localstack)
        logger.info("  Stopping %s service tasks...", service_name)
        ecs.update_service(cluster=cluster, service=service, desiredCount=0)
        self._wait_for_service(cluster, service, service_name, desired_running_count=0)
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

    def _wait_for_service(
        self,
        cluster: str,
        service: str,
        service_name: str,
        desired_running_count: int | None = None,
    ) -> None:
        """Block until an ECS service reaches the expected number of running tasks.

        With ``desired_running_count`` unset, waits for the service to run at
        least its configured ``desiredCount``. Passing ``0`` waits for every task
        to stop, which ``_start_service`` uses to confirm the scale-down took
        effect before a replacement task starts.

        Args:
            cluster (str): The ECS cluster name.
            service (str): The ECS service name.
            service_name (str): The human-readable service name for logs.
            desired_running_count (int | None): The expected running task count;
                when None the service's own ``desiredCount`` is used.

        Raises:
            InfrastructureError: If the service never reaches the expected count.

        """
        ecs = aws_client("ecs", localstack=self.localstack)
        state = (
            "RUNNING" if desired_running_count is None or desired_running_count > 0 else "STOPPED"
        )
        logger.info("  Waiting for %s service tasks to be %s...", service_name, state)
        for _ in range(SERVICE_WAIT_ATTEMPTS):
            services = ecs.describe_services(cluster=cluster, services=[service]).get(
                "services", []
            )
            if services:
                running = services[0].get("runningCount", 0)
                if desired_running_count is None:
                    if running >= services[0].get("desiredCount", 0):
                        logger.info("  %s service is RUNNING.", service_name)
                        return
                elif running == desired_running_count:
                    logger.info("  %s service is %s.", service_name, state)
                    return
            time.sleep(SERVICE_WAIT_INTERVAL)
        timeout = SERVICE_WAIT_ATTEMPTS * SERVICE_WAIT_INTERVAL
        message = f"{service_name} service did not reach {state} after {timeout} seconds."
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
        logger.info("  Backend: %s", self._app_url(alb_dns, "/status/"))
        logger.info("  Frontend: %s", self._app_url(alb_dns))
        logger.info("")
        logger.info("  Backend service: %s", backend_service)
        logger.info("  Frontend service: %s", frontend_service)
