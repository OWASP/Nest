"""Utilities for resolving and executing system commands."""

from __future__ import annotations

import shutil
import subprocess

from scripts.errors import CommandNotFoundError


class CommandRunner:
    """System command runner."""

    def require(self, cmd: str) -> str:
        """Return the absolute path to a command.

        Args:
            cmd (str): The name of the executable to find.

        Returns:
            str: The absolute path to the executable.

        Raises:
            CommandNotFoundError: If the command cannot be found on the system PATH.

        """
        path = shutil.which(cmd)
        if path is None:
            raise CommandNotFoundError(cmd)
        return path

    def run(
        self,
        command: str,
        *args: str,
        check: bool = False,
        capture_output: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        """Run a command.

        Args:
            command (str): The name of the executable to run.
            *args (str): Positional arguments to pass to the command.
            check (bool): Whether to raise an exception if the command exits with a non-zero status.
            capture_output (bool): Whether to capture stdout and stderr.

        Returns:
            subprocess.CompletedProcess[str]: The result of the executed command.

        """
        executable = self.require(command)
        return subprocess.run(
            [executable, *args],
            check=check,
            capture_output=capture_output,
            text=True,
        )
