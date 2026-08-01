"""Shared errors for the infrastructure scripts."""

from __future__ import annotations


class InfrastructureError(Exception):
    """Base error for infrastructure script failures."""

    __test__ = False


class CommandNotFoundError(InfrastructureError):
    """Raised when a required executable is missing from PATH."""

    def __init__(self, cmd: str) -> None:
        """Initialize the command not found error.

        Args:
            cmd (str): The name of the missing command.

        """
        super().__init__(f"required command '{cmd}' not found on PATH.")


class OverrideExistsError(InfrastructureError):
    """Raised when a test override file already exists on disk."""

    def __init__(self, filepath: str) -> None:
        """Initialize the override exists error.

        Args:
            filepath (str): The path to the conflicting override file.

        """
        super().__init__(f"{filepath} already exists. Refusing to run to avoid overwriting.")


class MissingAuthTokenError(InfrastructureError):
    """Raised when the LocalStack auth token is missing."""

    def __init__(self) -> None:
        """Initialize the missing auth token error."""
        super().__init__(
            "LOCALSTACK_AUTH_TOKEN environment variable is not set.\n"
            "A valid auth token is required to run LocalStack."
        )


class MissingEnvVarError(InfrastructureError):
    """Raised when a required environment variable is missing."""

    def __init__(self, env_var: str) -> None:
        """Initialize the missing environment variable error.

        Args:
            env_var (str): The name of the missing environment variable.

        """
        super().__init__(f"{env_var} is not set in the .env file.")
