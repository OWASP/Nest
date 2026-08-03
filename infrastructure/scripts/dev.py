"""Local development workflows for OWASP Nest."""

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from scripts.commands import CommandRunner
from scripts.errors import InfrastructureError, MissingEnvVarError
from scripts.load_env import LoadEnv
from scripts.localstack import LocalStack
from scripts.provision import ProvisionInfra

logger = logging.getLogger(__name__)

AUTH_TOKEN_ENV_VAR = "LOCALSTACK_AUTH_TOKEN"  # noqa: S105


class LocalInfrastructureRunner:
    """Orchestrator for local infrastructure workflows."""

    def __init__(
        self,
        commands: CommandRunner | None = None,
        *,
        localstack: LocalStack | None = None,
    ) -> None:
        """Initialize the local infrastructure runner.

        Args:
            commands (CommandRunner, optional): Command runner instance.
            localstack (LocalStack, optional): LocalStack manager instance.

        """
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.env_path = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(self.env_path)
        self.commands = commands or CommandRunner()
        self.localstack = localstack or LocalStack(self.commands)
        self.provisioner = ProvisionInfra(self.commands, localstack=self.localstack)
        self.loadenv = LoadEnv(localstack=self.localstack)

    def start_localstack(self) -> None:
        """Start LocalStack for local development.

        Raises:
            MissingEnvVarError: If the LOCALSTACK_AUTH_TOKEN is not set.
            InfrastructureError: If LocalStack fails to start or become ready.

        """
        if not os.environ.get(AUTH_TOKEN_ENV_VAR):
            raise MissingEnvVarError(AUTH_TOKEN_ENV_VAR)
        if self.localstack.healthy():
            logger.info("LocalStack is already running at %s.", self.localstack.api_url)
            return
        full_image, _ = self.localstack.image_info(self.root_dir)
        self.localstack.start(full_image)
        self.localstack.wait_ready()

    def stop_localstack(self) -> None:
        """Stop and remove the LocalStack container."""
        self.localstack.stop()

    def provision_infra(self) -> None:
        """Create resources on LocalStack and push the backend/frontend images."""
        self.provisioner.run()

    def load_env_params(self, *, dry_run: bool = False, overwrite: bool = False) -> None:
        """Upload local .env variables to the LocalStack SSM Parameter Store.

        Args:
            dry_run (bool): Print the parameters that would be uploaded instead of
                uploading them.
            overwrite (bool): Overwrite parameters that already exist.

        """
        self.loadenv.upload(dry_run=dry_run, overwrite=overwrite)


def main() -> None:
    """Bootstrap and run local infrastructure workflows."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description="Local infrastructure workflows")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("start-localstack", help="Start LocalStack")
    subparsers.add_parser("stop-localstack", help="Stop and remove LocalStack")
    subparsers.add_parser(
        "provision-infra",
        help="Create resources on LocalStack and push images",
    )

    load_env_params_parser = subparsers.add_parser(
        "load-env-params",
        help="Upload local .env variables to LocalStack SSM Parameter Store",
    )
    load_env_params_parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Print what would be uploaded without uploading",
    )
    load_env_params_parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="Overwrite existing parameters",
    )

    args = parser.parse_args()
    runner = LocalInfrastructureRunner()

    commands = {
        "start-localstack": runner.start_localstack,
        "stop-localstack": runner.stop_localstack,
        "provision-infra": runner.provision_infra,
    }

    try:
        if args.command == "load-env-params":
            runner.load_env_params(dry_run=args.dry_run, overwrite=args.overwrite)
        else:
            commands[args.command]()
    except InfrastructureError as exc:
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
