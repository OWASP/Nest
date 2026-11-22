"""Shared helpers for infrastructure scripts."""

import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from scripts.commands import CommandRunner
from scripts.errors import RunnerError


def configure_terraform_cache() -> None:
    """Create the Terraform plugin cache directory and export its path.

    Raises:
        OSError: If the plugin cache directory cannot be created.

    """
    cache_dir = Path.home() / ".terraform.d" / "plugin-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ["TF_PLUGIN_CACHE_DIR"] = str(cache_dir)


def chdir_repository_root(root_dir: Path) -> None:
    """Change the working directory to the repository root.

    Args:
        root_dir (Path): The repository root to change into.

    Raises:
        OSError: If the working directory cannot be changed.

    """
    os.chdir(root_dir)


def init_live_configuration(
    commands: CommandRunner,
    live_dir: Path,
    backend_config: str,
) -> None:
    """Initialize Terraform for the live/ configuration.

    Args:
        commands (CommandRunner): Command runner instance.
        live_dir (Path): The live/ Terraform configuration directory.
        backend_config (str): The Terraform backend configuration file name.

    Raises:
        RunnerError: If terraform init exits with a non-zero status.

    """
    result = commands.run(
        "tflocal",
        f"-chdir={live_dir}",
        "init",
        f"-backend-config={backend_config}",
        "-input=false",
        "-reconfigure",
        check=False,
    )
    if result.returncode != 0:
        message = f"terraform init failed in {live_dir}"
        raise RunnerError(message)


@contextmanager
def localstack_aws_env(api_url: str) -> Iterator[None]:
    """Set LocalStack-compatible AWS credentials for the duration of the context.

    Args:
        api_url (str): The LocalStack API URL to route AWS requests to.

    Yields:
        None: Control returns to the caller with the AWS environment set.

    """
    with (
        set_temporary_env("AWS_ACCESS_KEY_ID", "test"),
        set_temporary_env("AWS_ENDPOINT_URL", api_url),
        set_temporary_env("AWS_SECRET_ACCESS_KEY", "test"),
    ):
        yield


def read_live_output(
    commands: CommandRunner,
    live_dir: Path,
    name: str,
    *,
    json_output: bool = False,
) -> Any:
    """Read an output value from the live/ Terraform configuration.

    Args:
        commands (CommandRunner): Command runner instance.
        live_dir (Path): The live/ Terraform configuration directory.
        name (str): The Terraform output name.
        json_output (bool, optional): Whether to parse the value as JSON.
            Defaults to False.

    Returns:
        Any: The raw output value, or the parsed JSON value.

    Raises:
        RunnerError: If the terraform output command fails.

    """
    result = commands.run(
        "tflocal",
        f"-chdir={live_dir}",
        "output",
        "-json" if json_output else "-raw",
        name,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        message = f"terraform output failed for {name}: {result.stderr}"
        raise RunnerError(message)
    value = result.stdout.strip()
    return json.loads(value) if json_output else value


@contextmanager
def set_temporary_env(name: str, value: str) -> Iterator[None]:
    """Set an environment variable for the duration of the context.

    Args:
        name (str): The environment variable name.
        value (str): The value to set for the duration of the context.

    Yields:
        None: Control returns to the caller with the variable set.

    """
    previous_value = os.environ.get(name, None)
    os.environ[name] = value
    try:
        yield
    finally:
        if previous_value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = previous_value
