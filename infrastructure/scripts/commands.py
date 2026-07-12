"""Resolve executables from PATH and run them."""

from __future__ import annotations

import shutil
import subprocess

from scripts.errors import CommandNotFoundError


class CommandRunner:
    """Resolve executables from PATH and run them."""

    def require(self, cmd: str) -> str:
        """Return the absolute path to ``cmd``, or raise if it is not on PATH."""
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
        """Run an executable resolved from PATH with fixed argv arguments."""
        executable = self.require(command)
        return subprocess.run(
            [executable, *args],
            check=check,
            capture_output=capture_output,
            text=True,
        )
