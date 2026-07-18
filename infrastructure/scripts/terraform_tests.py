"""Discover and execute Terraform module tests."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from subprocess import CompletedProcess

from scripts.commands import CommandRunner
from scripts.errors import TestRunnerError

logger = logging.getLogger(__name__)

SEARCH_PATHS = ("infrastructure/bootstrap", "infrastructure/modules")


class TerraformTests:
    """Discover and execute Terraform module tests."""

    def __init__(
        self,
        commands: CommandRunner | None = None,
        *,
        search_paths: tuple[str, ...] = SEARCH_PATHS,
    ) -> None:
        """Initialize with command runner and search roots."""
        self.commands = commands or CommandRunner()
        self.search_paths = search_paths

    def discover_and_run(self, mode: str) -> None:
        """Discover and run Terraform tests for the given mode."""
        test_dirs = self.find_test_dirs()
        test_count = 0

        for test_dir in test_dirs:
            test_files = self.find_test_files(test_dir, mode)
            if not test_files:
                continue

            module_dir = str(Path(test_dir).parent)
            label = "integration" if mode == "integration" else "unit"
            logger.info("Testing %s for %s...", label, module_dir)
            self.run_module_tests(module_dir, test_files)
            test_count += 1

        if test_count == 0:
            message = f"No {mode} tests were found or executed."
            raise TestRunnerError(message)

    def find_test_dirs(self) -> list[str]:
        """Return sorted ``tests`` directories under the search roots."""
        test_dirs: list[str] = []
        for path in self.search_paths:
            root_path = Path(path)
            if not root_path.exists():
                continue
            for root, dirs, _filenames in os.walk(root_path):
                if ".terraform" not in root and "tests" in dirs:
                    test_dirs.append(str(Path(root) / "tests"))
        return sorted(test_dirs)

    @staticmethod
    def match_test_mode(entry: str, mode: str) -> bool:
        """Return whether a ``.tftest.hcl`` file belongs to the requested mode."""
        return entry == f"{mode}.tftest.hcl" or entry.endswith(f".{mode}.tftest.hcl")

    def find_test_files(self, test_dir: str, mode: str) -> list[str]:
        """Return sorted test filenames in ``test_dir`` for the given mode."""
        try:
            return sorted(
                entry.name
                for entry in Path(test_dir).iterdir()
                if entry.is_file() and self.match_test_mode(entry.name, mode)
            )
        except OSError as exc:
            message = f"could not read {test_dir}: {exc}"
            raise TestRunnerError(message) from exc

    @staticmethod
    def emit_output(result: CompletedProcess[str]) -> None:
        """Write captured Terraform output to the parent streams."""
        if result.stdout:
            sys.stdout.write(result.stdout)
        if result.stderr:
            sys.stderr.write(result.stderr)

    @staticmethod
    def failure_message(action: str, module_dir: str, result: CompletedProcess[str]) -> str:
        """Build a self-documenting failure message with Terraform diagnostics."""
        message = f"terraform {action} failed in {module_dir}"
        details = "\n".join(
            part.rstrip() for part in (result.stdout, result.stderr) if part and part.strip()
        )
        if details:
            return f"{message}\n{details}"
        return message

    def run_module_tests(self, module_dir: str, test_files: list[str]) -> None:
        """Initialize and test a Terraform module with the given filters."""
        init_result = self.commands.run(
            "terraform",
            f"-chdir={module_dir}",
            "init",
            "-backend=false",
            "-input=false",
            check=False,
            capture_output=True,
        )
        if init_result.returncode != 0:
            raise TestRunnerError(self.failure_message("init", module_dir, init_result))
        self.emit_output(init_result)

        filter_args = [f"-filter=tests/{test_file}" for test_file in test_files]
        test_result = self.commands.run(
            "terraform",
            f"-chdir={module_dir}",
            "test",
            *filter_args,
            check=False,
            capture_output=True,
        )
        if test_result.returncode != 0:
            raise TestRunnerError(self.failure_message("test", module_dir, test_result))
        self.emit_output(test_result)
