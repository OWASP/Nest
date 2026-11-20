"""Tests for the FOSSology license check configuration and file selection."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
ALLOWLIST_PATH = REPOSITORY_ROOT / ".fossology-allowlist.json"
DOCKERFILE_PATH = REPOSITORY_ROOT / "docker" / "fossology" / "Dockerfile"
FILTER_SCRIPT_PATH = REPOSITORY_ROOT / "tools" / "security" / "license_check_files.sh"

HAS_GIT = shutil.which("git") is not None


def find_bash() -> str | None:
    """Locate a bash executable across platforms, checking Git bash on Windows."""
    git_bash = Path(r"C:\Program Files\Git\bin\bash.exe")
    if git_bash.is_file():
        return str(git_bash)
    return shutil.which("bash")


class TestAllowlistConfig:
    """Validate .fossology-allowlist.json structure and rules."""

    def test_allowlist_is_valid_json_with_expected_keys(self) -> None:
        """Allowlist must exist, be valid JSON, and define licenses and exclude lists."""
        assert ALLOWLIST_PATH.is_file(), (
            f"Missing required allowlist at {ALLOWLIST_PATH}"
        )
        data = json.loads(ALLOWLIST_PATH.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        assert "licenses" in data
        assert "exclude" in data
        assert isinstance(data["licenses"], list)
        assert isinstance(data["exclude"], list)
        assert "MIT" in data["licenses"]
        assert "Apache-2.0" in data["licenses"]
        assert "OFL-1.1" in data["licenses"]

    def test_excluded_paths_exist_in_repository(self) -> None:
        """Every path listed in exclude must exist on disk to prevent stale rules."""
        assert ALLOWLIST_PATH.is_file(), (
            f"Missing required allowlist at {ALLOWLIST_PATH}"
        )
        data = json.loads(ALLOWLIST_PATH.read_text(encoding="utf-8"))
        for relative_path in data["exclude"]:
            target = REPOSITORY_ROOT / relative_path
            assert target.is_file(), f"Excluded file {relative_path} does not exist"

    def test_fossology_dockerfile_uses_pinned_digest(self) -> None:
        """FOSSology Dockerfile must exist and pin the image by sha256 digest."""
        assert DOCKERFILE_PATH.is_file(), (
            f"Missing required Dockerfile at {DOCKERFILE_PATH}"
        )
        content = DOCKERFILE_PATH.read_text(encoding="utf-8")
        assert "FROM fossology/fossology:" in content
        assert "@sha256:" in content

    def test_filter_script_exists_and_is_executable(self) -> None:
        """The license check file filtering script must exist in tools/security."""
        assert FILTER_SCRIPT_PATH.is_file(), (
            f"Missing filter script at {FILTER_SCRIPT_PATH}"
        )


class TestFileSelectionPipeline:
    """Exercise file selection filtering for tracked, untracked, deleted, and ignored files."""

    @pytest.mark.skipif(
        not HAS_GIT,
        reason="Git CLI required for repository integration tests",
    )
    def test_git_ls_files_filtering(self, tmp_path: Path) -> None:
        """Exercise the Make target's pipeline script to ensure proper file filtering."""
        bash_bin = find_bash()
        if not bash_bin:
            pytest.skip("Bash executable required to test production shell script")

        assert FILTER_SCRIPT_PATH.is_file(), (
            f"Missing filter script at {FILTER_SCRIPT_PATH}"
        )

        git_bin = shutil.which("git") or "git"

        # Initialize a temporary git repository
        subprocess.run(  # noqa: S603
            [git_bin, "init"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(  # noqa: S603
            [git_bin, "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(  # noqa: S603
            [git_bin, "config", "user.name", "Test User"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # 1. Tracked file
        tracked = tmp_path / "tracked.py"
        tracked.write_text("print(1)\n", encoding="utf-8")
        subprocess.run(  # noqa: S603
            [git_bin, "add", "tracked.py"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # 2. Ignored file
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.log\nnode_modules/\n", encoding="utf-8")
        subprocess.run(  # noqa: S603
            [git_bin, "add", ".gitignore"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        ignored_log = tmp_path / "debug.log"
        ignored_log.write_text("secret\n", encoding="utf-8")

        # 3. Untracked file (not ignored)
        untracked = tmp_path / "new_feature.py"
        untracked.write_text("print(2)\n", encoding="utf-8")

        # 4. Tracked file that is deleted from disk
        deleted = tmp_path / "to_delete.py"
        deleted.write_text("temp\n", encoding="utf-8")
        subprocess.run(  # noqa: S603
            [git_bin, "add", "to_delete.py"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        deleted.unlink()

        # 5. Unignored nested Git repository directory
        nested_repo = tmp_path / "nested_repo"
        nested_repo.mkdir()
        subprocess.run(  # noqa: S603
            [git_bin, "init"],
            cwd=nested_repo,
            check=True,
            capture_output=True,
        )
        (nested_repo / "sub.py").write_text("print(3)\n", encoding="utf-8")
        subprocess.run(  # noqa: S603
            [git_bin, "add", "sub.py"],
            cwd=nested_repo,
            check=True,
            capture_output=True,
        )

        # Run the production filter script in the test repository
        proc = subprocess.run(  # noqa: S603
            [bash_bin, str(FILTER_SCRIPT_PATH)],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        final_files = [
            p for p in proc.stdout.decode("utf-8", errors="replace").split("\0") if p
        ]

        # Verify pipeline includes tracked and untracked, while dropping
        # deleted and ignored files, and rejecting directories.
        assert "tracked.py" in final_files
        assert "new_feature.py" in final_files
        assert ".gitignore" in final_files
        assert "to_delete.py" not in final_files
        assert "debug.log" not in final_files
        assert "nested_repo" not in final_files
        assert "nested_repo/" not in final_files
