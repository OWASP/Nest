"""Serve MkDocs with live autoreload for local documentation.

Starts ``mkdocs serve`` and watches documentation sources. When a source file
changes, MkDocs is restarted so the preview stays in sync.
"""

from __future__ import annotations

import hashlib
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("mkdocs-serve")

DEBOUNCE_SECONDS = 1.0
MKDOCS_COMMAND = (
    "mkdocs",
    "serve",
    "-a",
    "0.0.0.0:8001",
    "-f",
    ".mkdocs.yaml",
)
POLL_SECONDS = 1.0
ROOT = Path(__file__).resolve().parent.parent
SKIP_DIR_NAMES = frozenset(
    {
        ".cache",
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "make",
        "site",
        "tests",
    }
)
SKIP_FILE_NAMES = frozenset(
    {
        "Makefile",
        "poetry.lock",
        "poetry.toml",
        "pyproject.toml",
        "serve.py",
    }
)
WATCH_PATHS = (
    ROOT / ".mkdocs.yaml",
    ROOT / "CODE_OF_CONDUCT.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "README.md",
    ROOT / "docs" / "src",
)


def iter_files(path: Path) -> list[Path]:
    """Return sorted documentation source files under path."""
    if path.is_file():
        return [path] if is_watched_file(path) else []
    if not path.is_dir():
        return []

    files: list[Path] = []
    for child in path.rglob("*"):
        if not child.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in child.parts):
            continue
        if not is_watched_file(child):
            continue
        files.append(child)
    return sorted(files)


def is_watched_file(path: Path) -> bool:
    """Return whether path should trigger an MkDocs restart."""
    if path.name in SKIP_FILE_NAMES:
        return False
    return path.suffix == ".md" or path.name == ".mkdocs.yaml"


def fingerprint() -> str:
    """Return a content hash of all watched documentation sources."""
    digest = hashlib.sha256()
    for path in WATCH_PATHS:
        for file_path in iter_files(path):
            digest.update(file_path.as_posix().encode())
            digest.update(b"\0")
            digest.update(file_path.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()


def start_mkdocs() -> subprocess.Popen[bytes]:
    """Start MkDocs in its own process group."""
    return subprocess.Popen(MKDOCS_COMMAND, start_new_session=True)  # noqa: S603


def stop_process(process: subprocess.Popen[bytes]) -> None:
    """Stop an MkDocs process group, forcing kill if it does not exit cleanly."""
    if process.poll() is not None:
        return

    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return

    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            return
        process.wait(timeout=5)


def wait_for_stable_fingerprint(current: str) -> str:
    """Wait until the fingerprint stops changing, then return the stable value."""
    while True:
        time.sleep(DEBOUNCE_SECONDS)
        try:
            latest = fingerprint()
        except OSError as error:
            logger.warning("Failed to fingerprint docs sources: %s", error)
            continue
        if latest == current:
            return latest
        current = latest


def main() -> None:
    """Run MkDocs and restart it whenever documentation sources change."""
    os.chdir(ROOT)
    previous = fingerprint()
    process = start_mkdocs()
    logger.info("Started MkDocs (pid %s)", process.pid)

    try:
        while True:
            time.sleep(POLL_SECONDS)

            if process.poll() is not None:
                logger.error("MkDocs exited with code %s", process.returncode)
                sys.exit(process.returncode or 1)

            try:
                current = fingerprint()
            except OSError as error:
                logger.warning("Failed to fingerprint docs sources: %s", error)
                continue

            if current == previous:
                continue

            current = wait_for_stable_fingerprint(current)
            if current == previous:
                continue

            previous = current
            logger.info("Docs sources changed; restarting MkDocs")
            stop_process(process)
            process = start_mkdocs()
            logger.info("Restarted MkDocs (pid %s)", process.pid)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        stop_process(process)


if __name__ == "__main__":
    main()
