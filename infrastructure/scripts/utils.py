"""Shared helpers for infrastructure scripts."""

import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


def configure_terraform_cache() -> None:
    """Create the Terraform plugin cache directory and export its path.

    Raises:
        OSError: If the plugin cache directory cannot be created.

    """
    cache_dir = Path.home() / ".terraform.d" / "plugin-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ["TF_PLUGIN_CACHE_DIR"] = str(cache_dir)


def enter_repo_root(root_dir: Path) -> None:
    """Change the working directory to the repository root.

    Args:
        root_dir (Path): The repository root to change into.

    Raises:
        OSError: If the working directory cannot be changed.

    """
    os.chdir(root_dir)


@contextmanager
def temporary_env(name: str, value: str) -> Iterator[None]:
    """Set an environment variable for the duration of the context.

    Args:
        name (str): The environment variable name.
        value (str): The value to set for the duration of the context.

    Yields:
        None: Control returns to the caller with the variable set.

    """
    previous = os.environ.get(name, None)
    os.environ[name] = value
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = previous
