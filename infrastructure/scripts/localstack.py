"""LocalStack lifecycle and Terraform override helpers for integration tests."""

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

_FROM_LOCALSTACK_RE = re.compile(r"^FROM\s+localstack/localstack(?:-pro)?:")
_FROM_LOCALSTACK_TAG_RE = re.compile(r"^FROM\s+localstack/localstack(?:-pro)?:\s*([^\s@]+)")


class LocalStack:
    """Manage LocalStack health checks and container lifecycle."""

    def __init__(
        self,
        commands: CommandRunner | None = None,
        *,
        container_name: str = LOCALSTACK_CONTAINER_NAME,
        host: str | None = None,
        port: int = LOCALSTACK_PORT,
    ) -> None:
        """Initialize LocalStack helpers.

        ``host`` defaults to ``LOCALSTACK_HOST`` from the environment, else localhost.
        """
        self.commands = commands or CommandRunner()
        self.container_name = container_name
        self.host = (
            host if host is not None else os.environ.get("LOCALSTACK_HOST", LOCALSTACK_HOST)
        )
        self.port = port

    @property
    def can_start_container(self) -> bool:
        """Return whether Docker is available to start a LocalStack container."""
        try:
            result = self.commands.run("docker", "info", check=False, capture_output=True)
        except CommandNotFoundError:
            return False
        return result.returncode == 0

    def info(self, *, log_error: bool = False) -> dict | None:
        """Return LocalStack info JSON, or ``None`` if unreachable."""
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
        """Return whether the LocalStack health endpoint responds successfully."""
        return self.info(log_error=log_error) is not None

    def license_activated(self, *, log_error: bool = False) -> bool:
        """Return whether LocalStack reports an activated license."""
        info = self.info(log_error=log_error)
        if info is None:
            return False
        return info.get("is_license_activated") is True

    def image_info(self, root_dir: str | Path) -> tuple[str, str]:
        """Return ``(full_image, tag)`` parsed from the LocalStack Dockerfile."""
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
        """Start a LocalStack container for integration tests."""
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
        """Block until LocalStack is healthy and its license is activated."""
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
    """Create and remove temporary Terraform override files."""

    def __init__(self, overrides: list[tuple[str, str]] | None = None) -> None:
        """Initialize with the override file mapping."""
        self.overrides = overrides if overrides is not None else OVERRIDES

    def check_absent(self) -> None:
        """Raise if any override file already exists on disk."""
        for filepath, _ in self.overrides:
            if Path(filepath).exists():
                raise OverrideExistsError(filepath)

    def write(self) -> None:
        """Write temporary Terraform override files for integration tests."""
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
        """Remove override files if they exist."""
        logger.info("Cleaning up override files...")
        for filepath, _ in self.overrides:
            path = Path(filepath)
            try:
                if path.exists():
                    path.unlink()
            except OSError as exc:
                logger.warning("Failed to remove %s: %s", filepath, exc)
