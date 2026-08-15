"""Infrastructure deployment orchestration utilities."""

import logging
from pathlib import Path

from scripts.commands import CommandRunner
from scripts.errors import RunnerError
from scripts.localstack import LocalStack
from scripts.utils import configure_terraform_cache, enter_repo_root, temporary_env

logger = logging.getLogger(__name__)


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

    def configure_environment(self) -> None:
        """Change to the repo root and configure the Terraform plugin cache."""
        enter_repo_root(self.root_dir)
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

        live_dir = self.root_dir / "infrastructure" / "live"
        with (
            temporary_env("AWS_ACCESS_KEY_ID", "test"),
            temporary_env("AWS_ENDPOINT_URL", self.localstack.api_url),
            temporary_env("AWS_SECRET_ACCESS_KEY", "test"),
        ):
            init_result = self.commands.run(
                "tflocal",
                f"-chdir={live_dir}",
                "init",
                "-backend-config=terraform.localstack.tfbackend",
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
                "-var-file=terraform.localstack.tfvars",
                check=False,
            )
            if apply_result.returncode != 0:
                message = f"terraform apply failed in {live_dir}"
                raise RunnerError(message)
        logger.info("Deployment on LocalStack successful!")
