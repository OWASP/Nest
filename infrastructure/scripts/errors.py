"""Shared errors for the infrastructure test runner."""

from __future__ import annotations


class TestRunnerError(Exception):
    """Base error for infrastructure test runner failures."""

    __test__ = False


class CommandNotFoundError(TestRunnerError):
    """Raised when a required executable is missing from PATH."""

    def __init__(self, cmd: str) -> None:
        """Record the missing command name."""
        super().__init__(f"required command '{cmd}' not found on PATH.")


class OverrideExistsError(TestRunnerError):
    """Raised when a test override file already exists on disk."""

    def __init__(self, filepath: str) -> None:
        """Record the conflicting override path."""
        super().__init__(f"{filepath} already exists. Refusing to run to avoid overwriting.")


class MissingAuthTokenError(TestRunnerError):
    """Raised when LocalStack auth is required but not configured."""

    def __init__(self) -> None:
        """Explain that LOCALSTACK_AUTH_TOKEN must be set."""
        super().__init__(
            "LOCALSTACK_AUTH_TOKEN environment variable is not set.\n"
            "LocalStack integration tests require a valid auth token to run."
        )
