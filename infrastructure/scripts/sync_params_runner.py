"""LocalStack SSM parameter synchronization orchestration."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from scripts.commands import CommandRunner
from scripts.constants import SOURCE_REPO_DIR
from scripts.errors import RunnerError

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_ENV_FILE = SOURCE_REPO_DIR / "backend" / ".env"
DEPLOYMENT_PARAMETERS = (
    "DJANGO_DB_HOST",
    "DJANGO_DB_PORT",
    "DJANGO_REDIS_AUTH_ENABLED",
    "DJANGO_REDIS_HOST",
    "DJANGO_REDIS_PORT",
    "DJANGO_REDIS_USE_TLS",
)
DEPLOYMENT_HOST = "localstack"
PARAMETERS_PAGE_QUERY = "{parameters: Parameters[].{name: Name, type: Type}, nextToken: NextToken}"
PARAMETERS_PAGE_SIZE = 10
PARAMETER_PATH = "/nest/production"
RDS_PORT_QUERY = "DBInstances[0].Endpoint.Port"
REDIS_PORT_QUERY = "CacheClusters[0].CacheNodes[0].Endpoint.Port"
SELECTOR_PARAMETERS = ("DJANGO_CONFIGURATION", "DJANGO_SETTINGS_MODULE")
SYNCED_PARAMETERS = (
    "DJANGO_ALLOWED_HOSTS",
    "DJANGO_ALGOLIA_APPLICATION_ID",
    "DJANGO_ALGOLIA_WRITE_API_KEY",
    "DJANGO_GITHUB_APP_ID",
    "DJANGO_GITHUB_APP_INSTALLATION_ID",
    "DJANGO_OPEN_AI_SECRET_KEY",
    "DJANGO_SECRET_KEY",
    "DJANGO_SENTRY_DSN",
    "DJANGO_SLACK_BOT_TOKEN",
    "DJANGO_SLACK_CLIENT_ID",
    "DJANGO_SLACK_CLIENT_SECRET",
    "DJANGO_SLACK_SEARCH_TOKEN",
    "DJANGO_SLACK_SIGNING_SECRET",
    "GITHUB_TOKEN",
)


def strip_surrounding_quotes(value: str) -> str:
    """Strip a matching pair of surrounding quotes from a value."""
    if len(value) > 1 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


class InfrastructureParameterSyncRunner:
    """SSM parameter sync runner orchestrator."""

    def __init__(
        self,
        *,
        commands: CommandRunner | None = None,
        env_file: Path | None = None,
    ) -> None:
        """Initialize the SSM parameter sync runner.

        Args:
            commands (CommandRunner, optional): Command runner instance.
            env_file (Path, optional): The .env file to read values from.
                Defaults to backend/.env inside the source repository mount.

        """
        self.commands = commands or CommandRunner()
        self.env_file = env_file or DEFAULT_ENV_FILE

    def fetch_deployment_endpoints(self) -> dict[str, str]:
        """Build deployment parameter values from the LocalStack-assigned ports.

        The host is the LocalStack compose service name, which is reachable
        from ECS task containers through Docker DNS. LocalStack serves Redis
        over plaintext without authentication.

        Returns:
            dict[str, str]: The deployment parameter names and values.

        Raises:
            RunnerError: If an awslocal endpoint command fails.

        """
        return {
            "DJANGO_DB_HOST": DEPLOYMENT_HOST,
            "DJANGO_DB_PORT": self.fetch_rds_port(),
            "DJANGO_REDIS_AUTH_ENABLED": "False",
            "DJANGO_REDIS_HOST": DEPLOYMENT_HOST,
            "DJANGO_REDIS_PORT": self.fetch_redis_port(),
            "DJANGO_REDIS_USE_TLS": "False",
        }

    def fetch_rds_port(self) -> str:
        """Fetch the LocalStack-assigned database port.

        Returns:
            str: The port the RDS instance is bound to.

        Raises:
            RunnerError: If awslocal rds describe-db-instances fails.

        """
        result = self.commands.run(
            "awslocal",
            "rds",
            "describe-db-instances",
            "--output",
            "json",
            "--query",
            RDS_PORT_QUERY,
            capture_output=True,
        )
        if result.returncode != 0:
            message = f"awslocal rds describe-db-instances failed: {result.stderr}"
            raise RunnerError(message)
        return str(json.loads(result.stdout))

    def fetch_redis_port(self) -> str:
        """Fetch the LocalStack-assigned Redis cache port.

        Returns:
            str: The port the Redis cache node is bound to.

        Raises:
            RunnerError: If awslocal elasticache describe-cache-clusters fails.

        """
        result = self.commands.run(
            "awslocal",
            "elasticache",
            "describe-cache-clusters",
            "--output",
            "json",
            "--query",
            REDIS_PORT_QUERY,
            "--show-cache-node-info",
            capture_output=True,
        )
        if result.returncode != 0:
            message = f"awslocal elasticache describe-cache-clusters failed: {result.stderr}"
            raise RunnerError(message)
        return str(json.loads(result.stdout))

    def list_parameters(self) -> list[dict[str, str]]:
        """List SSM parameters under the deployment path.

        Returns:
            list[dict[str, str]]: The parameter paths and types.

        Raises:
            RunnerError: If awslocal ssm get-parameters-by-path fails.

        """
        self.commands.require("awslocal")
        parameters: list[dict[str, str]] = []
        next_token: str | None = None
        while True:
            args = [
                "ssm",
                "get-parameters-by-path",
                "--max-results",
                str(PARAMETERS_PAGE_SIZE),
                "--output",
                "json",
                "--path",
                PARAMETER_PATH,
                "--query",
                PARAMETERS_PAGE_QUERY,
            ]
            if next_token is not None:
                args += ["--next-token", next_token]
            result = self.commands.run("awslocal", *args, capture_output=True)
            if result.returncode != 0:
                message = f"awslocal ssm get-parameters-by-path failed: {result.stderr}"
                raise RunnerError(message)

            page = json.loads(result.stdout)
            parameters.extend(page["parameters"])
            next_token = page.get("nextToken")
            if next_token is None:
                return parameters

    def put_parameter(self, *, name: str, parameter_type: str, value: str) -> None:
        """Write a value to an SSM parameter.

        Args:
            name (str): The full SSM parameter path.
            parameter_type (str): The SSM parameter type (String or SecureString).
            value (str): The value to write.

        Raises:
            RunnerError: If awslocal ssm put-parameter fails.

        """
        payload = json.dumps(
            {
                "Name": name,
                "Overwrite": True,
                "Type": parameter_type,
                "Value": value,
            }
        )
        result = self.commands.run(
            "awslocal",
            "ssm",
            "put-parameter",
            "--cli-input-json",
            payload,
            capture_output=True,
        )
        if result.returncode != 0:
            message = f"awslocal ssm put-parameter failed for {name}: {result.stderr}"
            raise RunnerError(message)

    def read_env_values(self) -> dict[str, str]:
        """Read environment values from the .env file.

        Returns:
            dict[str, str]: The environment variable names and values.

        Raises:
            RunnerError: If the .env file does not exist.

        """
        if not self.env_file.exists():
            message = f"environment file not found: {self.env_file}"
            raise RunnerError(message)

        values: dict[str, str] = {}
        for line in self.env_file.read_text().splitlines():
            entry = line.strip()
            if not entry or entry.startswith("#") or "=" not in entry:
                continue
            key, _, value = entry.partition("=")
            key = key.strip()
            value = strip_surrounding_quotes(value.strip())
            if not key or not value:
                continue
            values[key] = value
        return values

    def sync(
        self,
        *,
        configuration: str | None = None,
        settings_module: str | None = None,
    ) -> None:
        """Sync allow-listed and LocalStack-assigned endpoint values into SSM parameters.

        Args:
            configuration (str, optional): The Django configuration to set.
                Defaults to leaving the parameter unchanged.
            settings_module (str, optional): The Django settings module to set.
                Defaults to leaving the parameter unchanged.

        Raises:
            RunnerError: If the .env file is missing, an awslocal command fails,
                or an override has no matching SSM parameter.

        """
        env_values = self.read_env_values()
        parameters = self.list_parameters()
        parameter_names = {parameter["name"].rsplit("/", 1)[-1] for parameter in parameters}
        deployment_values = (
            self.fetch_deployment_endpoints()
            if any(name in parameter_names for name in DEPLOYMENT_PARAMETERS)
            else {}
        )
        overrides = {
            "DJANGO_CONFIGURATION": configuration,
            "DJANGO_SETTINGS_MODULE": settings_module,
        }
        missing_overrides = sorted(
            name
            for name, value in overrides.items()
            if value is not None and name not in parameter_names
        )
        if missing_overrides:
            message = f"no SSM parameter for override(s): {', '.join(missing_overrides)}"
            raise RunnerError(message)

        synced: list[str] = []
        not_allow_listed: list[str] = []
        without_env_values: list[str] = []
        for parameter in parameters:
            env_name = parameter["name"].rsplit("/", 1)[-1]
            if env_name in SELECTOR_PARAMETERS:
                value = overrides[env_name]
                if value is None:
                    logger.info("Skipping %s; pass an override to change it.", env_name)
                    continue
            elif env_name in DEPLOYMENT_PARAMETERS:
                value = deployment_values[env_name]
            elif env_name in SYNCED_PARAMETERS:
                value = env_values.get(env_name)
                if value is None:
                    without_env_values.append(env_name)
                    continue
            else:
                if env_name in env_values:
                    not_allow_listed.append(env_name)
                continue
            self.put_parameter(
                name=parameter["name"],
                parameter_type=parameter["type"],
                value=value,
            )
            synced.append(env_name)

        without_parameters = sorted((set(env_values) & set(SYNCED_PARAMETERS)) - parameter_names)
        missing_deployment = sorted(set(deployment_values) - parameter_names)
        logger.info("Synced %d parameters from %s.", len(synced), self.env_file)
        if deployment_values:
            logger.info(
                "Synced deployment endpoints: database %s:%s, Redis %s:%s.",
                DEPLOYMENT_HOST,
                deployment_values["DJANGO_DB_PORT"],
                DEPLOYMENT_HOST,
                deployment_values["DJANGO_REDIS_PORT"],
            )
        if not_allow_listed:
            logger.info("Skipped, not allow-listed: %s.", ", ".join(sorted(not_allow_listed)))
        if without_env_values:
            logger.info("No .env value for: %s.", ", ".join(sorted(without_env_values)))
        if without_parameters:
            logger.info("No SSM parameter for: %s.", ", ".join(without_parameters))
        if missing_deployment:
            logger.info(
                "No SSM parameter for deployment endpoint(s): %s.",
                ", ".join(missing_deployment),
            )

    def sync_deployment_endpoints(self) -> None:
        """Sync LocalStack-assigned endpoint values into their SSM parameters.

        Raises:
            RunnerError: If an awslocal command fails.

        """
        parameters = self.list_parameters()
        parameter_names = {parameter["name"].rsplit("/", 1)[-1] for parameter in parameters}
        missing = sorted(set(DEPLOYMENT_PARAMETERS) - parameter_names)
        if missing:
            logger.info(
                "No SSM parameter for deployment endpoint(s): %s.",
                ", ".join(missing),
            )
        deployment_values = (
            self.fetch_deployment_endpoints()
            if any(name in parameter_names for name in DEPLOYMENT_PARAMETERS)
            else {}
        )
        for parameter in parameters:
            env_name = parameter["name"].rsplit("/", 1)[-1]
            if env_name not in DEPLOYMENT_PARAMETERS:
                continue
            self.put_parameter(
                name=parameter["name"],
                parameter_type=parameter["type"],
                value=deployment_values[env_name],
            )
        if deployment_values:
            logger.info(
                "Synced deployment endpoints: database %s:%s, Redis %s:%s.",
                DEPLOYMENT_HOST,
                deployment_values["DJANGO_DB_PORT"],
                DEPLOYMENT_HOST,
                deployment_values["DJANGO_REDIS_PORT"],
            )
        else:
            logger.info("No deployment endpoint parameters found to sync.")
