"""Upload local .env variables to LocalStack SSM Parameter Store."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from botocore.exceptions import ClientError
from dotenv import dotenv_values

from scripts.aws import aws_client
from scripts.errors import MissingEnvFileError
from scripts.localstack import LocalStack

logger = logging.getLogger(__name__)

SECRET_NAME_HINTS = ("SECRET", "PASSWORD", "TOKEN", "KEY", "DSN")
SECURE_STRING = "SecureString"
PLAIN_STRING = "String"


def parameter_type(name: str) -> str:
    """Return the SSM parameter type for an environment variable name.

    Args:
        name (str): The environment variable name.

    Returns:
        str: ``SecureString`` for secret-like names, ``String`` otherwise.

    """
    upper = name.upper()
    if any(hint in upper for hint in SECRET_NAME_HINTS):
        return SECURE_STRING
    return PLAIN_STRING


class LoadEnv:
    """Upload local .env variables to LocalStack SSM Parameter Store."""

    def __init__(
        self,
        localstack: LocalStack | None = None,
        *,
        root_dir: Path | None = None,
    ) -> None:
        """Initialize the environment loader.

        Args:
            localstack (LocalStack, optional): The LocalStack manager. Defaults to
                a default ``LocalStack`` instance.
            root_dir (Path, optional): The project root. Defaults to the repository
                root relative to this module.

        """
        self.localstack = localstack or LocalStack()
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent.parent
        self.env_files = [
            self.root_dir / "backend" / ".env.localstack",
            self.root_dir / "frontend" / ".env.localstack",
        ]

    @property
    def prefix(self) -> str:
        """Return the SSM parameter prefix for the current environment."""
        return f"/nest/{os.environ.get('ENVIRONMENT', 'local')}"

    def get_env_vars(self, env_file: Path) -> dict[str, str]:
        """Parse a .env file into a dict of environment variables.

        Args:
            env_file (Path): The path to the .env file.

        Returns:
            dict[str, str]: A mapping of variable names to values.

        Raises:
            MissingEnvFileError: If ``env_file`` does not exist.

        """
        if not env_file.exists():
            raise MissingEnvFileError(str(env_file))
        return {
            name: value for name, value in dotenv_values(env_file).items() if value is not None
        }

    def upload(self, *, dry_run: bool = False, overwrite: bool = False) -> int:
        """Upload local .env variables to the LocalStack SSM Parameter Store.

        Args:
            dry_run (bool): Print the parameters that would be uploaded instead of
                uploading them.
            overwrite (bool): Overwrite parameters that already exist.

        Returns:
            int: The number of parameters uploaded.

        """
        uploaded = 0
        skipped = 0
        ssm_client = aws_client("ssm", localstack=self.localstack)
        for env_file in self.env_files:
            logger.info("Reading: %s", env_file)
            for name, value in self.get_env_vars(env_file).items():
                if not value:
                    logger.info(
                        "  SKIP: %s (empty value, SSM Parameter Store does not accept"
                        " empty value)",
                        name,
                    )
                    skipped += 1
                    continue

                param_name = f"{self.prefix}/{name}"
                param_type = parameter_type(name)
                if dry_run:
                    logger.info("  WOULD PUT: %s (%s)", param_name, param_type)
                    uploaded += 1
                    continue

                try:
                    ssm_client.put_parameter(
                        Name=param_name,
                        Value=value,
                        Type=param_type,
                        Overwrite=overwrite,
                    )
                except ClientError as exc:
                    if exc.response["Error"]["Code"] != "ParameterAlreadyExists":
                        raise
                    logger.info(
                        "  SKIP: %s (already exists, use --overwrite to force)",
                        param_name,
                    )
                    skipped += 1
                    continue

                logger.info("  PUT: %s (%s)", param_name, param_type)
                uploaded += 1

        logger.info("Done. %d parameters uploaded, %d skipped.", uploaded, skipped)
        return uploaded
