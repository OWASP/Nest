"""Infrastructure test orchestration utilities."""

from __future__ import annotations

import logging
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from scripts.commands import CommandRunner
from scripts.localstack import LocalStack, OverrideManager
from scripts.terraform_tests import ExecutionMode, TerraformTests

if TYPE_CHECKING:
    from collections.abc import Iterator

logger = logging.getLogger(__name__)


@contextmanager
def temporary_env(name: str, value: str) -> Iterator[None]:
    """Set an environment variable for the duration of the context."""
    previous = os.environ.get(name, None)
    os.environ[name] = value
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = previous


class InfrastructureTestRunner:
    """Infrastructure test runner orchestrator."""

    def __init__(
        self,
        root_dir: Path | None = None,
        *,
        commands: CommandRunner | None = None,
        localstack: LocalStack | None = None,
        overrides: OverrideManager | None = None,
        terraform_tests: TerraformTests | None = None,
    ) -> None:
        """Initialize the infrastructure test runner.

        Args:
            root_dir (Path, optional): The root directory of the project.
            commands (CommandRunner, optional): Command runner instance.
            localstack (LocalStack, optional): LocalStack manager instance.
            overrides (OverrideManager, optional): Terraform override manager instance.
            terraform_tests (TerraformTests, optional): Terraform test discovery and
                execution instance.

        """
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent.parent
        self.commands = commands or CommandRunner()
        self.localstack = localstack or LocalStack(self.commands)
        self.overrides = overrides or OverrideManager()
        self.terraform_tests = terraform_tests or TerraformTests(self.commands)

    def configure_environment(self) -> None:
        """Change to the repo root and configure the Terraform plugin cache."""
        os.chdir(self.root_dir)

        cache_dir = Path.home() / ".terraform.d" / "plugin-cache"
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            os.environ["TF_PLUGIN_CACHE_DIR"] = str(cache_dir)
        except OSError as exc:
            logger.warning("Could not configure TF_PLUGIN_CACHE_DIR: %s", exc)

    def print_localstack_tag(self) -> None:
        """Print the LocalStack image tag from the Dockerfile."""
        _, tag = self.localstack.image_info(self.root_dir)
        sys.stdout.write(f"{tag}\n")

    def print_localstack_image(self) -> None:
        """Print the full LocalStack image reference from the Dockerfile."""
        full_image, _ = self.localstack.image_info(self.root_dir)
        sys.stdout.write(f"{full_image}\n")

    def run_unit(self) -> None:
        """Run Terraform unit tests."""
        self.commands.require("terraform")
        self.terraform_tests.discover_and_run(ExecutionMode.UNIT)
        logger.info("All unit tests executed successfully!")

    def run_integration(self) -> None:
        """Run Terraform integration tests against LocalStack."""
        self.commands.require("terraform")
        self.overrides.check_absent()

        localstack_started = False
        try:
            if self.localstack.healthy():
                logger.info(
                    "Using already running LocalStack instance at %s.",
                    self.localstack.api_url,
                )
            elif self.localstack.can_start_container:
                logger.info(
                    "LocalStack is not running on port %s. Attempting to start it...",
                    self.localstack.port,
                )
                full_image, _ = self.localstack.image_info(self.root_dir)
                self.localstack.start(full_image)
                localstack_started = True
            else:
                logger.info(
                    "Waiting for external LocalStack at %s...",
                    self.localstack.api_url,
                )

            # Always wait: /_localstack/info can succeed before the Pro license activates.
            self.localstack.wait_ready()
            with temporary_env("AWS_ENDPOINT_URL", self.localstack.api_url):
                self.overrides.write()
                self.terraform_tests.discover_and_run(ExecutionMode.INTEGRATION)
                logger.info("All integration tests executed successfully!")
        finally:
            try:
                self.overrides.cleanup()
            finally:
                if localstack_started:
                    self.localstack.stop()
