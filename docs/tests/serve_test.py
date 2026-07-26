"""Tests for the local MkDocs serve helper."""

from __future__ import annotations

from pathlib import Path

import pytest

import serve


def test_is_watched_file_accepts_markdown(tmp_path: Path) -> None:
    assert serve.is_watched_file(tmp_path / "page.md") is True


def test_is_watched_file_accepts_mkdocs_config(tmp_path: Path) -> None:
    assert serve.is_watched_file(tmp_path / ".mkdocs.yaml") is True


def test_is_watched_file_skips_serve_script(tmp_path: Path) -> None:
    assert serve.is_watched_file(tmp_path / "serve.py") is False


def test_iter_files_skips_tests_but_includes_src_markdown(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    src = docs / "src"
    (src / "api").mkdir(parents=True)
    (docs / "tests").mkdir()
    (src / "api" / "README.md").write_text("# API\n", encoding="utf-8")
    (docs / "serve.py").write_text("print('serve')\n", encoding="utf-8")
    (docs / "tests" / "serve_test.py").write_text("def test_noop():\n    pass\n", encoding="utf-8")

    files = serve.iter_files(docs)

    assert files == [src / "api" / "README.md"]


def test_fingerprint_changes_when_markdown_changes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    src = tmp_path / "docs" / "src"
    src.mkdir(parents=True)
    page = src / "README.md"
    page.write_text("# One\n", encoding="utf-8")

    monkeypatch.setattr(serve, "ROOT", tmp_path)
    monkeypatch.setattr(serve, "WATCH_PATHS", (src,))

    first = serve.fingerprint()
    page.write_text("# Two\n", encoding="utf-8")
    second = serve.fingerprint()

    assert first != second
