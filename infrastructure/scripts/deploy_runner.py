"""Infrastructure deployment orchestration utilities."""

import logging
from pathlib import Path

from scripts.commands import CommandRunner
from scripts.errors import RunnerError
from scripts.localstack import LocalStack
from scripts.utils import chdir_repository_root, configure_terraform_cache, set_temporary_env

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
        localstack: LocalStack | None = None,
    ) -> None:
        """Initialize the infrastructure deployment orchestrator.

        Args:
            root_dir (Path, optional): The root directory of the project.
            commands (CommandRunner, optional): Command runner instance.
            localstack (LocalStack, optional): LocalStack manager instance.

        """
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent.parent
        self.commands = commands or CommandRunner()
        self.localstack = localstack or LocalStack(self.commands)

    def apply_live(self) -> None:
        """Initialize and apply the live/ Terraform configuration.

        Raises:
            RunnerError: If a Terraform command exits with a non-zero status.

        """
        live_dir = self.root_dir / "infrastructure" / "live"
        init_result = self.commands.run(
            "tflocal",
            f"-chdir={live_dir}",
            "init",
            f"-backend-config={LOCALSTACK_TFBACKEND}",
            "-input=false",
            "-reconfigure",
            check=False,
        )
        if init_result.returncode != 0:
            message = f"terraform init failed in {live_dir}"
            raise RunnerError(message)

        apply_result = self.commands.run(
            "tflocal",
            f"-chdir={live_dir}",
            "apply",
            "-auto-approve",
            "-input=false",
            f"-var-file={LOCALSTACK_TFVARS}",
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
        state_dir = self.root_dir / "infrastructure" / "state"
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
            self.apply_live()
        logger.info("Deployment on LocalStack successful!")
