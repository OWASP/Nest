"""Shared errors for the infrastructure runners."""

from __future__ import annotations


class RunnerError(Exception):
    """Base error for infrastructure runner failures."""

    __test__ = False


class CommandNotFoundError(RunnerError):
    """Raised when a required executable is missing from PATH."""

    def __init__(self, cmd: str) -> None:
        """Initialize the command not found error.

        Args:
            cmd (str): The name of the missing command.

        """
        super().__init__(f"required command '{cmd}' not found on PATH.")


class OverrideExistsError(RunnerError):
    """Raised when a test override file already exists on disk."""

    def __init__(self, filepath: str) -> None:
        """Initialize the override exists error.

        Args:
            filepath (str): The path to the conflicting override file.

        """
        super().__init__(f"{filepath} already exists. Refusing to run to avoid overwriting.")


class MissingAuthTokenError(RunnerError):
    """Raised when the LocalStack auth token is missing."""

    def __init__(self) -> None:
        """Initialize the missing auth token error."""
        super().__init__(
            "LOCALSTACK_AUTH_TOKEN environment variable is not set.\n"
            "LocalStack integration tests require a valid auth token to run."
        )
