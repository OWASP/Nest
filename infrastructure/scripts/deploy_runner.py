"""Infrastructure deployment orchestration."""

import logging
import time
from pathlib import Path

from scripts.commands import CommandRunner
from scripts.constants import (
    LIVE_DIR,
    LOCALSTACK_TFBACKEND,
    NEST_DUMP_OBJECT_KEY,
    SOURCE_REPO_DIR,
    STATE_DIR,
)
from scripts.errors import RunnerError
from scripts.images import IMAGE_CONFIG, ImageManager
from scripts.localstack import LocalStack
from scripts.sync_params_runner import InfrastructureParameterSyncRunner
from scripts.utils import (
    chdir_repository_root,
    configure_terraform_cache,
    init_live_configuration,
    localstack_aws_env,
    read_live_output,
)

logger = logging.getLogger(__name__)

LOCALSTACK_TFVARS = "terraform.localstack.tfvars"


class InfrastructureDeployRunner:
    """Infrastructure deployment orchestrator."""

    def __init__(
        self,
        root_dir: Path | None = None,
        *,
        commands: CommandRunner | None = None,
        images: ImageManager | None = None,
        localstack: LocalStack | None = None,
        parameter_sync: InfrastructureParameterSyncRunner | None = None,
    ) -> None:
        """Initialize the infrastructure deployment orchestrator.

        Args:
            root_dir (Path, optional): The root directory of the project.
            commands (CommandRunner, optional): Command runner instance.
            images (ImageManager, optional): ECR image manager instance.
            localstack (LocalStack, optional): LocalStack manager instance.
            parameter_sync (InfrastructureParameterSyncRunner, optional): SSM
                parameter sync runner instance.

        """
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent.parent
        self.commands = commands or CommandRunner()
        self.localstack = localstack or LocalStack(self.commands)
        self.images = images or ImageManager(
            self.root_dir,
            commands=self.commands,
        )
        self.parameter_sync = parameter_sync or InfrastructureParameterSyncRunner(
            commands=self.commands
        )

    def apply_live(
        self,
        *,
        refresh: bool = True,
        var_overrides: dict[str, str] | None = None,
    ) -> None:
        """Initialize and apply the live/ Terraform configuration.

        Args:
            refresh (bool): Whether Terraform should refresh state from the
                real infrastructure before planning. Defaults to True.
            var_overrides (dict[str, str], optional): Terraform variable
                values that take precedence over the tfvars file.

        Raises:
            RunnerError: If a Terraform command exits with a non-zero status.

        """
        self.init_live()
        live_dir = self.root_dir / LIVE_DIR
        apply_args = [
            "tflocal",
            f"-chdir={live_dir}",
            "apply",
            "-auto-approve",
            "-input=false",  # NOSONAR
            f"-var-file={LOCALSTACK_TFVARS}",
        ]
        for key, value in (var_overrides or {}).items():
            apply_args += ["-var", f"{key}={value}"]
        if not refresh:
            apply_args.append("-refresh=false")

        apply_result = self.commands.run(
            *apply_args,
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
        state_dir = self.root_dir / STATE_DIR
        init_result = self.commands.run(
            "tflocal",
            f"-chdir={state_dir}",
            "init",
            "-input=false",  # NOSONAR
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
            "-input=false",  # NOSONAR
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
            RunnerError: If any deployment step fails.

        """
        self.commands.require("tflocal")
        self.localstack.wait_ready()

        dump_path = SOURCE_REPO_DIR / "backend" / "data" / NEST_DUMP_OBJECT_KEY
        if not dump_path.is_file():
            message = f"{dump_path} not found. Run 'make fetch-nest-dump' and retry."
            raise RunnerError(message)

        with localstack_aws_env(self.localstack.api_url):
            self.apply_state()
            self.apply_live()
            self.upload_nest_dump(dump_path)
        logger.info("Deployment on LocalStack successful!")

    def init_live(self) -> None:
        """Initialize Terraform for the live/ configuration.

        Raises:
            RunnerError: If terraform init exits with a non-zero status.

        """
        live_dir = self.root_dir / LIVE_DIR
        init_live_configuration(self.commands, live_dir, LOCALSTACK_TFBACKEND)

    def push_images(self) -> dict[str, str]:
        """Build and push all service images to ECR.

        Returns:
            dict[str, str]: Mapping of service name to the pushed image tag.

        """
        self.images.login()
        tag = str(int(time.time()))
        for service in IMAGE_CONFIG:
            self.images.build(service, tag)
            self.images.push(service, tag)
        return dict.fromkeys(IMAGE_CONFIG, tag)

    def read_live_output(self, name: str) -> str:
        """Read a raw output value from the live/ Terraform configuration.

        Args:
            name (str): The Terraform output name.

        Returns:
            str: The raw output value.

        Raises:
            RunnerError: If the terraform output command fails.

        """
        return read_live_output(self.commands, self.root_dir / LIVE_DIR, name)

    def refresh(self) -> None:
        """Orchestrate a deployment refresh.

        Raises:
            RunnerError: If a Terraform command exits with a non-zero status.

        """
        self.commands.require("tflocal")
        self.localstack.wait_ready()

        with localstack_aws_env(self.localstack.api_url):
            self.init_live()
            tags = self.push_images()
            # TODO(rudransh-shrivastava): LocalStack updates port mappings,
            # computed endpoints, and more to its preferred configuration after terraform apply.
            # use -refresh=false to prevent updating them back.
            # Ideal fix is to pass LocalStack preferred configuration via tfvars.
            self.apply_live(
                refresh=False,
                var_overrides={f"{svc}_image_tag": tag for svc, tag in tags.items()},
            )
            self.parameter_sync.sync_deployment_endpoints()
        logger.info("Deployment on LocalStack successful!")

    def upload_nest_dump(self, dump_path: Path) -> None:
        """Upload the nest.dump fixture to the LocalStack fixtures bucket.

        Args:
            dump_path (Path): The local dump file to upload.

        Raises:
            RunnerError: If the S3 upload fails.

        """
        bucket = self.read_live_output("fixtures_bucket_name")
        destination = f"s3://{bucket}/{NEST_DUMP_OBJECT_KEY}"
        result = self.commands.run(
            "awslocal",
            "s3",
            "cp",
            str(dump_path),
            destination,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            message = f"upload to {destination} failed: {result.stderr}"
            raise RunnerError(message)
        logger.info("Uploaded %s to %s.", NEST_DUMP_OBJECT_KEY, destination)
