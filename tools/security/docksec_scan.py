"""Scan Dockerfiles with DockSec.

This script runs inside the pinned DockSec image. It stays on the standard
library so that image's Python 3.12 can execute it. ``docksec`` is invoked
from the image ``PATH``; this module does not start Docker itself.
"""

from __future__ import annotations

import argparse
import logging
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path

logger = logging.getLogger(__name__)

DOCKERFILE_DIRECTORIES = ("docker", ".clusterfuzzlite")
SCAN_OPTIONS = (
    "--scan-only",
    "--offline",
    "--no-config",
    "--fail-on",
    "HIGH",
    "--format",
    "json",
)

CommandRunner = Callable[[Sequence[str]], int]


class DocksecScanError(Exception):
    """Raised when DockSec cannot finish the file scan."""

    def __init__(self, message: str, *, exit_code: int = 1) -> None:
        """Store the message and the process exit code to return."""
        super().__init__(message)
        self.exit_code = exit_code


def is_regular_file(path: Path) -> bool:
    """Return whether ``path`` is a file and not a symlink."""
    return path.is_file() and not path.is_symlink()


def is_dockerfile(name: str) -> bool:
    """Return whether ``name`` is a Dockerfile or a ``Dockerfile.*`` variant."""
    return name == "Dockerfile" or name.startswith("Dockerfile.")


def discover_dockerfiles(root: Path) -> list[Path]:
    """Return Dockerfiles under ``docker/`` and ``.clusterfuzzlite/``, sorted."""
    paths: list[Path] = []
    for directory_name in DOCKERFILE_DIRECTORIES:
        directory = root / directory_name
        if not directory.is_dir():
            continue
        paths.extend(
            path
            for path in directory.rglob("*")
            if is_regular_file(path) and is_dockerfile(path.name)
        )
    return sorted(paths, key=lambda path: path.as_posix())


def relative_path(root: Path, path: Path) -> str:
    """Return ``path`` relative to ``root``, using forward slashes."""
    return path.relative_to(root).as_posix()


def dockerfile_command(path: str) -> list[str]:
    """Return the DockSec command for one Dockerfile."""
    return ["docksec", path, *SCAN_OPTIONS]


def run_command(args: Sequence[str], *, cwd: Path) -> int:
    """Run a command in ``cwd`` and return its exit code."""
    try:
        completed = subprocess.run(list(args), check=False, cwd=cwd)  # noqa: S603
    except FileNotFoundError as error:
        message = f"Command not found: {args[0]}"
        raise DocksecScanError(message) from error
    return completed.returncode


class DocksecFileScanner:
    """Run DockSec against Dockerfiles in a repository."""

    def __init__(self, root: Path, *, runner: CommandRunner | None = None) -> None:
        """Scan ``root``. ``runner`` replaces the ``docksec`` process in tests."""
        self.root = root
        self._runner = runner

    def run(self, args: Sequence[str]) -> int:
        """Run ``args`` with the injected runner, or ``docksec`` in the repository."""
        if self._runner is not None:
            return self._runner(args)
        return run_command(args, cwd=self.root)

    def scan(self) -> None:
        """Scan every Dockerfile, then fail once if any scan failed.

        Raises:
            DocksecScanError: No Dockerfiles were found, or DockSec failed.
                The exit code is the highest DockSec status from the run.

        """
        dockerfiles = discover_dockerfiles(self.root)
        if not dockerfiles:
            message = "No Dockerfiles found."
            raise DocksecScanError(message)

        failures: list[tuple[str, int]] = []
        for path in dockerfiles:
            display, status = self.scan_dockerfile(path)
            if status != 0:
                failures.append((display, status))

        if not failures:
            return

        worst_exit = max(status for _, status in failures)
        failed = ", ".join(f"{display} (exit {status})" for display, status in failures)
        message = f"DockSec failed for {failed}."
        raise DocksecScanError(message, exit_code=worst_exit)

    def scan_dockerfile(self, path: Path) -> tuple[str, int]:
        """Scan one Dockerfile and return its path and DockSec exit code."""
        display = relative_path(self.root, path)
        logger.info("Scanning Dockerfile %s...", display)
        status = self.run(dockerfile_command(display))
        if status != 0:
            logger.error("DockSec failed for %s with exit %s.", display, status)
        return display, status


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Report DockSec findings for Dockerfiles.",
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        help="Repository root (default: current directory)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Scan Dockerfiles. Return the process exit code."""
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    root = args.repository_root if args.repository_root is not None else Path.cwd()
    try:
        DocksecFileScanner(root).scan()
    except DocksecScanError as error:
        failure = error
    else:
        return 0
    logger.error("%s", failure)
    return failure.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
