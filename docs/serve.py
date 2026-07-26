"""Serve MkDocs with live autoreload for local documentation.

Starts ``mkdocs serve`` and watches documentation sources. When a source file
changes, MkDocs is restarted so the preview stays in sync.
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
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
DOCS_SRC = ROOT / "docs" / "src"
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
SNIPPET_INCLUDE_RE = re.compile(
    r"""--8<--\s*["']([^"':]+)(?::[^"']+)?["']""",
)  # pymdownx snippet path, optional section after colon
WATCHED_SUFFIXES = frozenset(
    {
        ".gif",
        ".jpeg",
        ".jpg",
        ".md",
        ".png",
        ".svg",
        ".webp",
        ".yaml",
        ".yml",
    }
)
WATCH_PATHS = (
    ROOT / ".mkdocs.yaml",
    DOCS_SRC,
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
    if path.name == ".mkdocs.yaml":
        return True
    return path.suffix.lower() in WATCHED_SUFFIXES


def snippet_include_paths(docs_src: Path | None = None) -> list[Path]:
    """Return repo-root paths included by pymdownx snippets under docs_src."""
    docs_src = DOCS_SRC if docs_src is None else docs_src
    includes: set[Path] = set()
    if not docs_src.is_dir():
        return []

    for stub in docs_src.rglob("*.md"):
        if any(part in SKIP_DIR_NAMES for part in stub.parts):
            continue
        try:
            text = stub.read_text(encoding="utf-8")
        except OSError as error:
            logger.warning("Failed to read docs stub %s: %s", stub, error)
            continue
        for match in SNIPPET_INCLUDE_RE.finditer(text):
            include_path = ROOT / match.group(1)
            if include_path.is_file():
                includes.add(include_path)
            else:
                logger.warning("Snippet include not found: %s (from %s)", include_path, stub)

    return sorted(includes)


def watch_paths() -> list[Path]:
    """Return paths whose changes should restart MkDocs."""
    paths: list[Path] = []
    seen: set[Path] = set()
    for path in (*WATCH_PATHS, *snippet_include_paths()):
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        paths.append(path)
    return paths


def fingerprint() -> str:
    """Return a content hash of all watched documentation sources."""
    digest = hashlib.sha256()
    for path in watch_paths():
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
