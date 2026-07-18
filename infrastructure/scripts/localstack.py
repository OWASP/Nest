"""LocalStack and Terraform override utilities."""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import time
from http import HTTPStatus
from http.client import HTTPConnection, HTTPException
from pathlib import Path

from scripts.commands import CommandRunner
from scripts.errors import (
    CommandNotFoundError,
    MissingAuthTokenError,
    OverrideExistsError,
    TestRunnerError,
)

logger = logging.getLogger(__name__)

LOCALSTACK_CONTAINER_NAME = "nest-localstack"
LOCALSTACK_HOST = "localhost"
LOCALSTACK_PORT = 4566
LOCALSTACK_INFO_PATH = "/_localstack/info"
HEALTH_MAX_ATTEMPTS = 30
HEALTH_POLL_INTERVAL = 2
LICENSE_MAX_ATTEMPTS = 15

_FROM_LOCALSTACK_RE = re.compile(r"^FROM\s+localstack/localstack(?:-pro)?:")
_FROM_LOCALSTACK_TAG_RE = re.compile(r"^FROM\s+localstack/localstack(?:-pro)?:\s*([^\s@]+)")


class LocalStack:
    """LocalStack container manager."""

    def __init__(
        self,
        commands: CommandRunner | None = None,
        *,
        container_name: str = LOCALSTACK_CONTAINER_NAME,
        host: str | None = None,
        port: int = LOCALSTACK_PORT,
    ) -> None:
        """Initialize the LocalStack container manager.

        Args:
            commands (CommandRunner, optional): Command runner instance.
            container_name (str): The name for the LocalStack Docker container.
            host (str, optional): The host address for LocalStack. Defaults to
                the LOCALSTACK_HOST environment variable or localhost.
            port (int): The port for LocalStack.

        """
        self.commands = commands or CommandRunner()
        self.container_name = container_name
        self.host = (
            host if host is not None else os.environ.get("LOCALSTACK_HOST", LOCALSTACK_HOST)
        )
        self.port = port
        self.api_url = f"http://{self.host}:{self.port}"  # NOSONAR

    @property
    def can_start_container(self) -> bool:
        """Return whether Docker is available to start a LocalStack container."""
        try:
            result = self.commands.run("docker", "info", check=False, capture_output=True)
        except CommandNotFoundError:
            return False
        return result.returncode == 0

    def info(self, *, log_error: bool = False) -> dict | None:
        """Return LocalStack info JSON.

        Args:
            log_error (bool, optional): Whether to log a warning if the request fails. Defaults to False.

        Returns:
            dict | None: The info JSON payload, or None if unreachable.

        """
        connection = HTTPConnection(self.host, self.port, timeout=2)
        try:
            connection.request("GET", LOCALSTACK_INFO_PATH)
            response = connection.getresponse()
            if response.status != HTTPStatus.OK:
                return None
            return json.loads(response.read().decode("utf-8"))
        except (OSError, HTTPException, UnicodeDecodeError, json.JSONDecodeError) as exc:
            if log_error:
                logger.warning("LocalStack info request failed: %s", exc)
            return None
        finally:
            connection.close()

    def healthy(self, *, log_error: bool = False) -> bool:
        """Return whether the LocalStack health endpoint responds successfully.

        Args:
            log_error (bool, optional): Whether to log a warning if the request fails. Defaults to False.

        Returns:
            bool: True if the endpoint responds successfully, False otherwise.

        """
        return self.info(log_error=log_error) is not None

    def license_activated(self, *, log_error: bool = False) -> bool:
        """Return whether LocalStack reports an activated license.

        Args:
            log_error (bool, optional): Whether to log a warning if the request fails. Defaults to False.

        Returns:
            bool: True if the license is activated, False otherwise.

        """
        info = self.info(log_error=log_error)
        if info is None:
            return False
        return info.get("is_license_activated") is True

    def image_info(self, root_dir: str | Path) -> tuple[str, str]:
        """Return image info parsed from the LocalStack Dockerfile.

        Args:
            root_dir (str | Path): The root directory of the project.

        Returns:
            tuple[str, str]: A tuple containing the full image reference and the tag.

        Raises:
            TestRunnerError: If the Dockerfile cannot be read or the image cannot be determined.

        """
        dockerfile_path = Path(root_dir) / "docker" / "localstack" / "Dockerfile"
        if not dockerfile_path.exists():
            message = f"Dockerfile not found at {dockerfile_path}"
            raise TestRunnerError(message)

        content = dockerfile_path.read_text(encoding="utf-8")

        # Assumes a single-stage Dockerfile; update if a multi-stage build is introduced.
        match_line = next(
            (line for line in content.splitlines() if _FROM_LOCALSTACK_RE.match(line)),
            None,
        )
        if match_line is None:
            message = f"could not determine LocalStack image from {dockerfile_path}."
            raise TestRunnerError(message)

        full_image = re.sub(r"^FROM\s+", "", match_line).strip()
        match_tag = _FROM_LOCALSTACK_TAG_RE.search(match_line)
        if match_tag is None:
            message = f"could not determine LocalStack image tag from {dockerfile_path}."
            raise TestRunnerError(message)

        return full_image, match_tag.group(1)

    def start(self, image: str) -> None:
        """Start a LocalStack container.

        Args:
            image (str): The Docker image reference to start.

        Raises:
            MissingAuthTokenError: If the LOCALSTACK_AUTH_TOKEN is not set.
            TestRunnerError: If the container fails to start.

        """
        if not os.environ.get("LOCALSTACK_AUTH_TOKEN"):
            raise MissingAuthTokenError

        self.commands.run("docker", "rm", "-f", self.container_name, check=False)

        logger.info("Starting LocalStack container...")
        # Forward the token via the process environment (-e NAME) rather than argv.
        # ECR_ENDPOINT_STRATEGY=off avoids *.localhost.localstack.cloud DNS during teardown.
        try:
            self.commands.run(
                "docker",
                "run",
                "-d",
                "--name",
                self.container_name,
                "-p",
                f"{self.port}:{LOCALSTACK_PORT}",
                "-e",
                "ECR_ENDPOINT_STRATEGY=off",
                "-e",
                "LOCALSTACK_AUTH_TOKEN",
                image,
                check=True,
            )
        except (CommandNotFoundError, subprocess.CalledProcessError) as exc:
            message = f"Error starting LocalStack container: {exc}"
            raise TestRunnerError(message) from exc

    def stop(self) -> None:
        """Stop and remove the LocalStack container (best-effort)."""
        logger.info("Stopping and removing LocalStack container...")
        self.commands.run("docker", "stop", self.container_name, check=False)
        self.commands.run("docker", "rm", self.container_name, check=False)

    def wait_ready(self) -> None:
        """Block until LocalStack is healthy and its license is activated.

        Raises:
            TestRunnerError: If LocalStack fails to become healthy or activate its license within the timeout.

        """
        logger.info("Waiting for LocalStack to become healthy...")
        for attempt in range(1, HEALTH_MAX_ATTEMPTS + 1):
            if self.healthy():
                break
            if attempt == HEALTH_MAX_ATTEMPTS:
                self.healthy(log_error=True)
                timeout = HEALTH_MAX_ATTEMPTS * HEALTH_POLL_INTERVAL
                message = f"LocalStack failed to become healthy within {timeout} seconds."
                raise TestRunnerError(message)
            logger.info("Waiting... (attempt %s/%s)", attempt, HEALTH_MAX_ATTEMPTS)
            time.sleep(HEALTH_POLL_INTERVAL)

        logger.info("Waiting for LocalStack license activation...")
        for attempt in range(1, LICENSE_MAX_ATTEMPTS + 1):
            if self.license_activated():
                break
            if attempt == LICENSE_MAX_ATTEMPTS:
                self.license_activated(log_error=True)
                if self.can_start_container:
                    self.commands.run(
                        "docker",
                        "logs",
                        "--tail",
                        "30",
                        self.container_name,
                        check=False,
                    )
                timeout = LICENSE_MAX_ATTEMPTS * HEALTH_POLL_INTERVAL
                message = f"LocalStack license failed to activate within {timeout} seconds."
                raise TestRunnerError(message)
            time.sleep(HEALTH_POLL_INTERVAL)

        logger.info("LocalStack is ready!")


class OverrideManager:
    """Terraform override manager."""

    # Temporary Terraform overrides that disable prevent_destroy during integration tests.
    OVERRIDES: list[tuple[str, str]] = [
        (
            "infrastructure/modules/storage/modules/s3-bucket/test_override.tf",
            "aws_s3_bucket.this",
        ),
        (
            "infrastructure/modules/storage/modules/shared-data-bucket/test_override.tf",
            "aws_s3_bucket.nest_shared_data",
        ),
    ]

    def __init__(self, overrides: list[tuple[str, str]] | None = None) -> None:
        """Initialize the override manager.

        Args:
            overrides (list[tuple[str, str]], optional): A list of (filepath, resource_address)
                tuples. Defaults to the standard OVERRIDES mapping.

        """
        self.overrides = overrides if overrides is not None else self.OVERRIDES

    def check_absent(self) -> None:
        """Ensure no override files already exist on disk.

        Raises:
            OverrideExistsError: If any override file is found.

        """
        for filepath, _ in self.overrides:
            if Path(filepath).exists():
                raise OverrideExistsError(filepath)

    def write(self) -> None:
        """Write temporary Terraform override files.

        Raises:
            TestRunnerError: If an override file cannot be written.

        """
        logger.info("Writing override files...")
        for filepath, resource in self.overrides:
            resource_type, _, resource_name = resource.partition(".")
            content = (
                f'resource "{resource_type}" "{resource_name}" {{\n'
                f"  lifecycle {{\n"
                f"    prevent_destroy = false\n"
                f"  }}\n"
                f"}}\n"
            )
            path = Path(filepath)
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            except OSError as exc:
                message = f"Error writing override file {filepath}: {exc}"
                raise TestRunnerError(message) from exc

    def cleanup(self) -> None:
        """Clean up temporary override files."""
        logger.info("Cleaning up override files...")
        for filepath, _ in self.overrides:
            path = Path(filepath)
            try:
                if path.exists():
                    path.unlink()
            except OSError as exc:
                logger.warning("Failed to remove %s: %s", filepath, exc)
