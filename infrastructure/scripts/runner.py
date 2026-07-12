"""Orchestrate infrastructure unit and integration test runs."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from scripts.commands import CommandRunner
from scripts.localstack import LocalStack, OverrideManager
from scripts.terraform_tests import TerraformTests

logger = logging.getLogger(__name__)


class InfrastructureTestRunner:
    """Orchestrate infrastructure unit and integration test runs."""

    def __init__(
        self,
        root_dir: Path | None = None,
        *,
        commands: CommandRunner | None = None,
        localstack: LocalStack | None = None,
        overrides: OverrideManager | None = None,
        terraform_tests: TerraformTests | None = None,
    ) -> None:
        """Wire collaborators for a repository root."""
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

    def run_unit(self) -> None:
        """Run Terraform unit tests."""
        self.commands.require("terraform")
        self.terraform_tests.discover_and_run("unit")
        logger.info("All unit tests executed successfully!")

    def run_integration(self) -> None:
        """Run Terraform integration tests against LocalStack."""
        self.commands.require("terraform")
        self.overrides.check_absent()

        localstack_started = False
        try:
            if self.localstack.healthy():
                logger.info(
                    "Using already running LocalStack instance at %s:%s.",
                    self.localstack.host,
                    self.localstack.port,
                )
            elif self.localstack.can_start_container:
                logger.info(
                    "LocalStack is not running on port %s. Attempting to start it...",
                    self.localstack.port,
                )
                full_image, _ = self.localstack.image_info(self.root_dir)
                self.localstack.start(full_image)
                localstack_started = True
                self.localstack.wait_ready()
            else:
                logger.info(
                    "Waiting for external LocalStack at %s:%s...",
                    self.localstack.host,
                    self.localstack.port,
                )
                self.localstack.wait_ready()

            self.overrides.write()
            self.terraform_tests.discover_and_run("integration")
            logger.info("All integration tests executed successfully!")
        finally:
            self.overrides.cleanup()
            if localstack_started:
                self.localstack.stop()
