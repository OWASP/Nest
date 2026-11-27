"""FOSSology license compliance check."""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path

logger = logging.getLogger(__name__)

ALLOWLIST_NAME = ".fossology-allowlist.json"
DOCKERFILE_PATH = Path("docker/fossology/Dockerfile")
FOSSOLOGY_FROM_PREFIX = "FROM fossology/fossology:"
SCANNER_ENTRYPOINT = "/bin/fossologyscanner"
SCANNER_ARGS = ("nomos", "ojo", "repo")

CommandRunner = Callable[[Sequence[str]], int]


class FossologyLicenseCheckError(Exception):
    """Raised when the license check cannot finish."""

    def __init__(self, message: str, *, exit_code: int = 1) -> None:
        """Store the message and the process exit code to return."""
        super().__init__(message)
        self.exit_code = exit_code


class FossologyLicenseChecker:
    """Run the FOSSology license scanners against repository files."""

    def __init__(
        self,
        root: Path,
        *,
        runner: CommandRunner | None = None,
        path_lister: Callable[[Path], list[str]] | None = None,
    ) -> None:
        """Initialize the FOSSology license checker."""
        self.root = root
        self._runner = runner
        self._path_lister = path_lister

    def read_image(self) -> str:
        """Return the pinned FOSSology image reference from the repository Dockerfile."""
        dockerfile = self.root / DOCKERFILE_PATH
        if not dockerfile.is_file():
            message = f"Missing {dockerfile}"
            raise FossologyLicenseCheckError(message)
        for line in dockerfile.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith(FOSSOLOGY_FROM_PREFIX):
                return stripped.removeprefix("FROM ").strip()
        message = f"No FOSSology FROM line in {dockerfile}"
        raise FossologyLicenseCheckError(message)

    def list_repository_paths(self) -> list[str]:
        """Return git-tracked and unignored untracked paths under the repository root."""
        if self._path_lister is not None:
            return self._path_lister(self.root)
        try:
            completed = subprocess.run(
                ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],  # noqa: S607
                cwd=self.root,
                check=True,
                capture_output=True,
            )
        except FileNotFoundError as error:
            message = "git is required for the FOSSology license check"
            raise FossologyLicenseCheckError(message) from error
        except subprocess.CalledProcessError as error:
            detail = error.stderr.decode("utf-8", errors="replace").strip() or str(error)
            message = f"git ls-files failed: {detail}"
            raise FossologyLicenseCheckError(message) from error
        return [path for path in completed.stdout.decode("utf-8").split("\0") if path]

    def select_scannable_paths(self, relative_paths: Sequence[str]) -> list[str]:
        """Return relative paths that exist as regular non-symlink files."""
        selected: list[str] = []
        for relative in relative_paths:
            path = self.root / relative
            if path.is_file() and not path.is_symlink():
                selected.append(relative)
        return selected

    def stage_scan_tree(self, relative_paths: Sequence[str], destination: Path) -> None:
        """Copy ``relative_paths`` from the repository into ``destination``."""
        for relative in relative_paths:
            source = self.root / relative
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(source, target)
            except OSError as error:
                message = f"Failed to copy {relative}: {error}"
                raise FossologyLicenseCheckError(message) from error

    def run(self, args: Sequence[str]) -> int:
        """Run ``args`` with the injected runner, or ``subprocess`` on the host."""
        if self._runner is not None:
            return self._runner(args)
        try:
            completed = subprocess.run(list(args), check=False)  # noqa: S603
        except FileNotFoundError as error:
            message = f"Command not found: {args[0]}"
            raise FossologyLicenseCheckError(message) from error
        return completed.returncode

    def check(self) -> None:
        """Stage scannable files and run FOSSology."""
        allowlist = self.root / ALLOWLIST_NAME
        if not allowlist.is_file():
            message = f"Missing {ALLOWLIST_NAME}"
            raise FossologyLicenseCheckError(message)

        relative_paths = self.select_scannable_paths(self.list_repository_paths())
        if not relative_paths:
            message = "No scannable files found for the FOSSology license check"
            raise FossologyLicenseCheckError(message)

        image = self.read_image()
        # ignore_cleanup_errors: results/ may be root-owned if the scanner ignores --user.
        with tempfile.TemporaryDirectory(
            prefix="fossology-license-",
            ignore_cleanup_errors=True,
        ) as temporary:
            scan_root = Path(temporary)
            results_dir = scan_root / "results"
            results_dir.mkdir()
            self.stage_scan_tree(relative_paths, scan_root)
            command = [
                "docker",
                "run",
                "--rm",
                "--platform",
                "linux/amd64",
                "--user",
                f"{os.getuid()}:{os.getgid()}",
                "--entrypoint",
                SCANNER_ENTRYPOINT,
                f"-v={scan_root}:/src:ro",
                # Writable overlay so root-owned results do not block host cleanup.
                f"-v={results_dir}:/src/results",
                f"-v={allowlist}:/allowlist.json:ro",
                "-w=/src",
                image,
                *SCANNER_ARGS,
                "--allowlist-path",
                "/allowlist.json",
            ]
            logger.info("Running FOSSology license check on %s files...", len(relative_paths))
            status = self.run(command)
            if status != 0:
                message = f"FOSSology license check failed with exit {status}."
                raise FossologyLicenseCheckError(message, exit_code=status)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the license check. Return the process exit code."""
    parser = argparse.ArgumentParser(
        description="Check repository files for licenses outside the FOSSology allowlist.",
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        help="Repository root (default: current directory)",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    root = args.repository_root if args.repository_root is not None else Path.cwd()
    try:
        FossologyLicenseChecker(root.resolve()).check()
    except FossologyLicenseCheckError as error:
        logger.exception("FOSSology license check failed")
        return error.exit_code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
