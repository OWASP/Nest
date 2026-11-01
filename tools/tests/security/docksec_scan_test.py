"""Tests for the DockSec file scan."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest

from docksec_scan import (
    SCAN_OPTIONS,
    DocksecFileScanner,
    DocksecScanError,
    discover_dockerfiles,
    dockerfile_command,
    main,
    run_command,
)


def write_file(path: Path, content: str = "FROM scratch\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


class RecordingRunner:
    """Records DockSec commands and returns scripted exit codes."""

    def __init__(self, exits: dict[str, int] | None = None) -> None:
        self.exits = exits or {}
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, args: Sequence[str]) -> int:
        self.calls.append(tuple(args))
        return self.exits.get(args[1], 0)


def scanner(root: Path, runner: RecordingRunner) -> DocksecFileScanner:
    return DocksecFileScanner(root, runner=runner)


class TestDiscoverDockerfiles:
    def test_finds_dockerfiles_and_variants_in_sorted_order(self, tmp_path: Path) -> None:
        write_file(tmp_path / "docker" / "frontend" / "Dockerfile")
        write_file(tmp_path / "docker" / "backend" / "Dockerfile.tests")
        write_file(tmp_path / ".clusterfuzzlite" / "Dockerfile")
        write_file(tmp_path / "docker" / "notes.txt", "ignore\n")
        write_file(tmp_path / "docker" / "dockerfile", "ignore\n")
        write_file(tmp_path / "elsewhere" / "Dockerfile")

        discovered = discover_dockerfiles(tmp_path)

        assert [path.relative_to(tmp_path).as_posix() for path in discovered] == [
            ".clusterfuzzlite/Dockerfile",
            "docker/backend/Dockerfile.tests",
            "docker/frontend/Dockerfile",
        ]

    def test_skips_symlink(self, tmp_path: Path) -> None:
        target = tmp_path / "docker" / "real" / "Dockerfile"
        write_file(target)
        link = tmp_path / "docker" / "linked" / "Dockerfile"
        link.parent.mkdir(parents=True)
        link.symlink_to(target)

        discovered = discover_dockerfiles(tmp_path)

        assert discovered == [target]

    def test_returns_empty_when_directories_are_missing(self, tmp_path: Path) -> None:
        assert discover_dockerfiles(tmp_path) == []


class TestCommands:
    def test_scan_options_fail_on_high(self) -> None:
        assert SCAN_OPTIONS == (
            "--scan-only",
            "--offline",
            "--no-config",
            "--fail-on",
            "HIGH",
            "--format",
            "json",
        )

    def test_dockerfile_command_uses_report_only_flags(self) -> None:
        command = dockerfile_command("docker/backend/Dockerfile")

        assert command == ["docksec", "docker/backend/Dockerfile", *SCAN_OPTIONS]


class TestDocksecFileScanner:
    def test_scans_dockerfiles_and_skips_compose(self, tmp_path: Path) -> None:
        write_file(tmp_path / "docker" / "backend" / "Dockerfile")
        write_file(tmp_path / "docker" / "frontend" / "Dockerfile.local")
        write_file(tmp_path / "docker-compose" / "local" / "compose.yaml", "services: {}\n")
        runner = RecordingRunner()

        scanner(tmp_path, runner).scan()

        assert runner.calls == [
            tuple(dockerfile_command("docker/backend/Dockerfile")),
            tuple(dockerfile_command("docker/frontend/Dockerfile.local")),
        ]

    def test_scan_continues_and_returns_the_highest_exit(self, tmp_path: Path) -> None:
        write_file(tmp_path / "docker" / "backend" / "Dockerfile")
        write_file(tmp_path / "docker" / "frontend" / "Dockerfile")
        runner = RecordingRunner(
            {
                "docker/backend/Dockerfile": 1,
                "docker/frontend/Dockerfile": 3,
            }
        )

        with pytest.raises(DocksecScanError) as error:
            scanner(tmp_path, runner).scan()

        assert error.value.exit_code == 3
        assert "docker/backend/Dockerfile (exit 1)" in str(error.value)
        assert "docker/frontend/Dockerfile (exit 3)" in str(error.value)
        assert runner.calls == [
            tuple(dockerfile_command("docker/backend/Dockerfile")),
            tuple(dockerfile_command("docker/frontend/Dockerfile")),
        ]

    def test_missing_dockerfiles_fail(self, tmp_path: Path) -> None:
        write_file(tmp_path / "docker-compose" / "local" / "compose.yaml", "services: {}\n")

        with pytest.raises(DocksecScanError, match=r"No Dockerfiles found\.") as error:
            scanner(tmp_path, RecordingRunner()).scan()

        assert error.value.exit_code == 1


class TestRunCommand:
    def test_returns_exit_code(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        captured: dict[str, object] = {}

        class Result:
            returncode = 3

        def fake_run(args: list[str], *, check: bool, cwd: Path) -> Result:
            captured["args"] = args
            captured["check"] = check
            captured["cwd"] = cwd
            return Result()

        monkeypatch.setattr("docksec_scan.subprocess.run", fake_run)

        status = run_command(["docksec", "Dockerfile"], cwd=tmp_path)

        assert status == 3
        assert captured == {"args": ["docksec", "Dockerfile"], "check": False, "cwd": tmp_path}

    def test_missing_command_raises(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        def fake_run(args: list[str], **_kwargs: object) -> None:
            raise FileNotFoundError(args[0])

        monkeypatch.setattr("docksec_scan.subprocess.run", fake_run)

        with pytest.raises(DocksecScanError, match="Command not found: docksec") as error:
            run_command(["docksec", "Dockerfile"], cwd=tmp_path)

        assert error.value.exit_code == 1


class TestMain:
    def test_returns_zero_when_the_scan_succeeds(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        def succeed(_scanner: DocksecFileScanner) -> None:
            return

        monkeypatch.setattr(DocksecFileScanner, "scan", succeed)

        assert main(["--repository-root", str(tmp_path)]) == 0

    def test_returns_scanner_exit_code(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        def fail(_scanner: DocksecFileScanner) -> None:
            message = "DockSec failed for docker/backend/Dockerfile (exit 3)."
            raise DocksecScanError(message, exit_code=3)

        monkeypatch.setattr(DocksecFileScanner, "scan", fail)

        assert main(["--repository-root", str(tmp_path)]) == 3
