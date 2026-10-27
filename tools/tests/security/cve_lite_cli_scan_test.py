"""Exercise the CVE Lite CLI scan script with a controlled scanner executable."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

SCAN_SCRIPT = Path(__file__).resolve().parents[2] / "security" / "cve_lite_cli_scan.sh"
PROJECTS = (".", "cspell", "e2e", "frontend")


class TestCveLiteCliScan:
    """Tests for the CVE Lite CLI scan script."""

    @pytest.fixture
    def scan_environment(self, tmp_path: Path) -> dict[str, str]:
        """Provide four lockfiles and a scanner that records calls and simulates failures."""
        for project in PROJECTS:
            directory = tmp_path / project
            directory.mkdir(exist_ok=True)
            (directory / "pnpm-lock.yaml").touch()

        bin_directory = tmp_path / "bin"
        bin_directory.mkdir()
        executable = bin_directory / "cve-lite"
        executable.write_text(
            "#!/bin/sh\n"
            'printf "%s\\n" "$*" >> "$SCAN_CALLS"\n'
            '[ -f "$1/pnpm-lock.yaml" ] || exit 2\n'
            'case "$1" in\n'
            '  "$FAIL_PROJECT") exit "$FAIL_STATUS" ;;\n'
            '  "$OTHER_FAIL_PROJECT") exit "$OTHER_FAIL_STATUS" ;;\n'
            "esac\n"
            "exit 0\n"
        )
        executable.chmod(0o755)
        return {
            **os.environ,
            "PATH": str(bin_directory),
            "SCAN_CALLS": str(tmp_path / "calls.txt"),
            "FAIL_PROJECT": "",
            "FAIL_STATUS": "0",
            "OTHER_FAIL_PROJECT": "",
            "OTHER_FAIL_STATUS": "0",
        }

    @pytest.mark.parametrize(
        ("failed_project", "failed_status", "other_project", "other_status", "expected"),
        [
            ("", 0, "", 0, 0),
            (".", 1, "", 0, 1),
            ("frontend", 1, "", 0, 1),
            (".", 3, "frontend", 1, 3),
            ("cspell", 1, "e2e", 3, 3),
        ],
    )
    def test_scans_every_lockfile_and_preserves_failures(
        self,
        tmp_path: Path,
        scan_environment: dict[str, str],
        failed_project: str,
        failed_status: int,
        other_project: str,
        other_status: int,
        expected: int,
    ) -> None:
        """A finding or incomplete scan must not hide failures or skip later projects."""
        scan_environment.update(
            FAIL_PROJECT=failed_project,
            FAIL_STATUS=str(failed_status),
            OTHER_FAIL_PROJECT=other_project,
            OTHER_FAIL_STATUS=str(other_status),
        )

        result = subprocess.run(  # noqa: S603
            ["/bin/sh", str(SCAN_SCRIPT)],
            cwd=tmp_path,
            env=scan_environment,
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == expected, result.stderr
        calls = Path(scan_environment["SCAN_CALLS"]).read_text().splitlines()
        assert [call.split()[0] for call in calls] == list(PROJECTS)
        for call in calls:
            assert call.split()[1:] == [
                "--all",
                "--cache-dir",
                ".cache/cve-lite",
                "--fail-on",
                "medium",
                "--incomplete-policy",
                "error",
                "--verbose",
            ]

    def test_missing_scanner_fails(self, tmp_path: Path, scan_environment: dict[str, str]) -> None:
        """An unavailable scanner must never produce a successful security check."""
        (tmp_path / "bin" / "cve-lite").unlink()

        result = subprocess.run(  # noqa: S603
            ["/bin/sh", str(SCAN_SCRIPT)],
            cwd=tmp_path,
            env=scan_environment,
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 127
