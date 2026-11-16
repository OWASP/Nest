"""Exercise the FOSSology scan script with a real repository and a controlled scanner."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

GIT = "/usr/bin/git"
SCAN_SCRIPT = Path(__file__).resolve().parents[2] / "security" / "fossology_scan.sh"


class TestFossologyScan:
    """Tests for the FOSSology scan script."""

    @pytest.fixture
    def repository(self, tmp_path: Path) -> Path:
        """Provide a repository with tracked, untracked, ignored, and locally deleted files."""
        root = tmp_path / "repository"
        (root / "nested").mkdir(parents=True)
        (root / ".fossology-allowlist.json").write_text('{"licenses": ["MIT"]}\n')
        (root / ".gitignore").write_text("ignored.txt\n")
        (root / "deleted.txt").write_text("deleted\n")
        (root / "nested" / "with space.txt").write_text("nested\n")
        (root / "tracked.txt").write_text("tracked\n")

        git = [GIT, "-C", str(root), "-c", "user.name=test", "-c", "user.email=test@example.com"]
        subprocess.run([*git, "init", "-q"], check=True)  # noqa: S603
        subprocess.run([*git, "add", "."], check=True)  # noqa: S603
        subprocess.run([*git, "commit", "-q", "-m", "init"], check=True)  # noqa: S603

        (root / "deleted.txt").unlink()
        (root / "ignored.txt").write_text("ignored\n")
        (root / "untracked.txt").write_text("untracked\n")
        return root

    @pytest.fixture
    def scan_environment(self, tmp_path: Path) -> dict[str, str]:
        """Provide a scanner that records its arguments and the files it received."""
        executable = tmp_path / "fossologyscanner"
        executable.write_text(
            "#!/bin/sh\n"
            'printf "%s\\n" "$*" > "$SCAN_ARGS"\n'
            'find . -type f | sort > "$SCAN_FILES"\n'
            'exit "$SCAN_STATUS"\n'
        )
        executable.chmod(0o755)
        return {
            **os.environ,
            "FOSSOLOGY_SCANNER": str(executable),
            "SCAN_ARGS": str(tmp_path / "args.txt"),
            "SCAN_FILES": str(tmp_path / "files.txt"),
            "SCAN_STATUS": "0",
        }

    def run_scan(
        self, repository: Path, scan_environment: dict[str, str]
    ) -> subprocess.CompletedProcess[str]:
        """Run the script with the same file list the security-license-check target uses."""
        files = subprocess.run(  # noqa: S603
            [GIT, "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=repository,
            capture_output=True,
            check=True,
        ).stdout
        return subprocess.run(  # noqa: S603
            ["/bin/bash", str(SCAN_SCRIPT), str(repository)],
            input=files.decode(),
            env=scan_environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_scans_tracked_and_untracked_files_only(
        self, repository: Path, scan_environment: dict[str, str]
    ) -> None:
        """Ignored and locally deleted files are skipped, everything else is scanned."""
        result = self.run_scan(repository, scan_environment)

        assert result.returncode == 0, result.stderr
        assert Path(scan_environment["SCAN_FILES"]).read_text().splitlines() == [
            "./.fossology-allowlist.json",
            "./.gitignore",
            "./nested/with space.txt",
            "./tracked.txt",
            "./untracked.txt",
        ]
        assert Path(scan_environment["SCAN_ARGS"]).read_text().split() == [
            "nomos",
            "ojo",
            "repo",
            "--allowlist-path",
            f"{repository}/.fossology-allowlist.json",
        ]

    @pytest.mark.parametrize("status", [1, 2])
    def test_scanner_findings_fail_the_check(
        self, repository: Path, scan_environment: dict[str, str], status: int
    ) -> None:
        """A license finding or scanner error must fail the check."""
        scan_environment["SCAN_STATUS"] = str(status)

        assert self.run_scan(repository, scan_environment).returncode == status

    @pytest.mark.skipif(os.geteuid() == 0, reason="root can read files without permission")
    def test_copy_error_fails_before_scanning(
        self, repository: Path, scan_environment: dict[str, str]
    ) -> None:
        """A file that cannot be copied must never produce a clean scan of a partial tree."""
        (repository / "tracked.txt").chmod(0)

        result = self.run_scan(repository, scan_environment)

        assert result.returncode != 0
        assert not Path(scan_environment["SCAN_ARGS"]).exists()

    def test_missing_allowlist_fails_before_scanning(
        self, repository: Path, scan_environment: dict[str, str]
    ) -> None:
        """Without the allowlist every license would be reported, so fail early instead."""
        (repository / ".fossology-allowlist.json").unlink()

        result = self.run_scan(repository, scan_environment)

        assert result.returncode == 1
        assert "Missing .fossology-allowlist.json" in result.stderr
        assert not Path(scan_environment["SCAN_ARGS"]).exists()
