"""Tests for the FOSSology license compliance check."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest

from fossology_license_check import (
    ALLOWLIST_NAME,
    DOCKERFILE_PATH,
    SCANNER_ARGS,
    SCANNER_ENTRYPOINT,
    FossologyLicenseChecker,
    FossologyLicenseCheckError,
    main,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
ALLOWLIST_PATH = REPOSITORY_ROOT / ALLOWLIST_NAME


class RecordingRunner:
    """Record docker commands and return a scripted exit code."""

    def __init__(self, exit_code: int = 0) -> None:
        self.exit_code = exit_code
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, args: Sequence[str]) -> int:
        self.calls.append(tuple(args))
        return self.exit_code


def write_fixture(root: Path) -> list[str]:
    """Create a minimal repo fixture and return scannable relative paths."""
    (root / "nested").mkdir(parents=True)
    (root / ALLOWLIST_NAME).write_text('{"licenses": ["MIT"], "exclude": []}\n')
    (root / "docker" / "fossology").mkdir(parents=True)
    (root / DOCKERFILE_PATH).write_text(
        "FROM fossology/fossology:4.7.3-scanner@sha256:abc\n",
        encoding="utf-8",
    )
    (root / "nested" / "with space.txt").write_text("nested\n", encoding="utf-8")
    (root / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    return [ALLOWLIST_NAME, "docker/fossology/Dockerfile", "nested/with space.txt", "tracked.txt"]


class TestFossologyLicenseCheck:
    """Tests for ``FossologyLicenseChecker``."""

    def test_allowlist_and_dockerfile(self) -> None:
        data = json.loads(ALLOWLIST_PATH.read_text(encoding="utf-8"))
        assert set(data["licenses"]) >= {"Apache-2.0", "MIT", "OFL-1.1"}
        assert isinstance(data["exclude"], list)
        for relative_path in data["exclude"]:
            assert (REPOSITORY_ROOT / relative_path).is_file()

        dockerfile = REPOSITORY_ROOT / DOCKERFILE_PATH
        content = dockerfile.read_text(encoding="utf-8")
        assert "FROM fossology/fossology:" in content
        assert "@sha256:" in content

    def test_list_repository_paths_uses_git(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        recorded: dict[str, object] = {}

        def fake_run(args: Sequence[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
            recorded["args"] = tuple(args)
            recorded["cwd"] = kwargs.get("cwd")
            return subprocess.CompletedProcess(
                args=list(args),
                returncode=0,
                stdout=b"tracked.txt\0",
                stderr=b"",
            )

        monkeypatch.setattr("fossology_license_check.subprocess.run", fake_run)

        assert FossologyLicenseChecker(tmp_path).list_repository_paths() == ["tracked.txt"]
        assert recorded["args"] == (
            "git",
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
        )
        assert recorded["cwd"] == tmp_path

    def test_select_scannable_paths(self, tmp_path: Path) -> None:
        paths = write_fixture(tmp_path)
        (tmp_path / "gone.txt").write_text("x\n", encoding="utf-8")
        (tmp_path / "gone.txt").unlink()
        (tmp_path / "dir").mkdir()
        link = tmp_path / "link.txt"
        link.symlink_to(tmp_path / "tracked.txt")

        selected = FossologyLicenseChecker(tmp_path).select_scannable_paths(
            [*paths, "gone.txt", "dir", "link.txt"]
        )

        assert selected == paths
        assert "gone.txt" not in selected
        assert "dir" not in selected
        assert "link.txt" not in selected

    def test_stage_scan_tree(self, tmp_path: Path) -> None:
        root = tmp_path / "repo"
        destination = tmp_path / "scan"
        write_fixture(root)
        destination.mkdir()

        FossologyLicenseChecker(root).stage_scan_tree(
            ["tracked.txt", "nested/with space.txt"],
            destination,
        )

        assert (destination / "tracked.txt").read_text(encoding="utf-8") == "tracked\n"
        assert (destination / "nested" / "with space.txt").read_text(
            encoding="utf-8"
        ) == "nested\n"

    def test_check_runs_docker(self, tmp_path: Path) -> None:
        paths = write_fixture(tmp_path)
        runner = RecordingRunner()

        FossologyLicenseChecker(tmp_path, runner=runner, path_lister=lambda _: paths).check()

        assert len(runner.calls) == 1
        command = runner.calls[0]
        assert command[0] == "docker"
        assert "--platform" in command
        assert "linux/amd64" in command
        assert "--user" in command
        assert SCANNER_ENTRYPOINT in command
        assert any(arg.endswith(":/src:ro") for arg in command)
        assert any(arg.endswith(":/src/results") for arg in command)
        assert "fossology/fossology:4.7.3-scanner@sha256:abc" in command
        assert all(arg in command for arg in SCANNER_ARGS)
        assert "--allowlist-path" in command

    def test_check_failures(self, tmp_path: Path) -> None:
        paths = write_fixture(tmp_path)

        runner = RecordingRunner(exit_code=2)
        scanner_failure = FossologyLicenseChecker(
            tmp_path, runner=runner, path_lister=lambda _: paths
        )
        with pytest.raises(FossologyLicenseCheckError) as raised:
            scanner_failure.check()
        assert raised.value.exit_code == 2

        (tmp_path / ALLOWLIST_NAME).unlink()
        runner = RecordingRunner()
        missing_allowlist = FossologyLicenseChecker(
            tmp_path, runner=runner, path_lister=lambda _: paths
        )
        with pytest.raises(FossologyLicenseCheckError, match="Missing"):
            missing_allowlist.check()
        assert runner.calls == []

    def test_main_returns_scanner_exit_code(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        write_fixture(tmp_path)

        def fail_check(_self: FossologyLicenseChecker) -> None:
            message = "failed"
            raise FossologyLicenseCheckError(message, exit_code=2)

        monkeypatch.setattr(FossologyLicenseChecker, "check", fail_check)
        assert main(["--repository-root", str(tmp_path)]) == 2
