"""Utilities for resolving and executing system commands."""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import TYPE_CHECKING

from scripts.errors import CommandNotFoundError

if TYPE_CHECKING:
    from pathlib import Path


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
        cwd: str | Path | None = None,
        input_data: str | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """Run a command.

        Args:
            command (str): The name of the executable to run.
            *args (str): Positional arguments to pass to the command.
            check (bool): Whether to raise an exception if the command exits with a
                non-zero status.
            capture_output (bool): Whether to capture stdout and stderr.
            cwd (str | Path, optional): The working directory to run the command in.
            input_data (str, optional): Data to write to the command's stdin.
            env (dict[str, str], optional): Extra environment variables to merge over
                the current process environment.

        Returns:
            subprocess.CompletedProcess[str]: The result of the executed command.

        """
        executable = self.require(command)
        merged_env = {**os.environ, **env} if env else None
        return subprocess.run(  # noqa: S603
            [executable, *args],
            check=check,
            capture_output=capture_output,
            text=True,
            cwd=cwd,
            input=input_data,
            env=merged_env,
        )
