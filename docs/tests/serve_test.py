"""Tests for the local MkDocs serve helper."""

from __future__ import annotations

from pathlib import Path

import pytest

import serve


def test_is_watched_file_accepts_markdown(tmp_path: Path) -> None:
    assert serve.is_watched_file(tmp_path / "page.md") is True


def test_is_watched_file_accepts_png_assets(tmp_path: Path) -> None:
    assert serve.is_watched_file(tmp_path / "logo.png") is True


def test_is_watched_file_accepts_mkdocs_config(tmp_path: Path) -> None:
    assert serve.is_watched_file(tmp_path / ".mkdocs.yaml") is True


def test_is_watched_file_skips_serve_script(tmp_path: Path) -> None:
    assert serve.is_watched_file(tmp_path / "serve.py") is False


def test_iter_files_skips_tests_but_includes_src_markdown_and_assets(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    src = docs / "src"
    assets = src / "assets" / "images"
    assets.mkdir(parents=True)
    (docs / "tests").mkdir()
    (src / "api" / "README.md").parent.mkdir(parents=True)
    (src / "api" / "README.md").write_text("# API\n", encoding="utf-8")
    (assets / "logo.png").write_bytes(b"\x89PNG\r\n")
    (docs / "serve.py").write_text("print('serve')\n", encoding="utf-8")
    (docs / "tests" / "serve_test.py").write_text("def test_noop():\n    pass\n", encoding="utf-8")

    files = serve.iter_files(docs)

    assert files == [src / "api" / "README.md", assets / "logo.png"]


def test_snippet_include_paths_resolves_external_sources(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path
    docs_src = root / "docs" / "src" / "backend"
    docs_src.mkdir(parents=True)
    included = root / "backend" / "README.md"
    included.parent.mkdir(parents=True)
    included.write_text("# Backend\n", encoding="utf-8")
    (docs_src / "README.md").write_text('--8<-- "backend/README.md"\n', encoding="utf-8")

    monkeypatch.setattr(serve, "ROOT", root)

    assert serve.snippet_include_paths(root / "docs" / "src") == [included]


def test_fingerprint_changes_when_markdown_changes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    src = tmp_path / "docs" / "src"
    src.mkdir(parents=True)
    page = src / "README.md"
    page.write_text("# One\n", encoding="utf-8")

    monkeypatch.setattr(serve, "ROOT", tmp_path)
    monkeypatch.setattr(serve, "DOCS_SRC", src)
    monkeypatch.setattr(serve, "WATCH_PATHS", (src,))

    first = serve.fingerprint()
    page.write_text("# Two\n", encoding="utf-8")
    second = serve.fingerprint()

    assert first != second


def test_fingerprint_changes_when_snippet_include_changes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path
    docs_src = root / "docs" / "src"
    docs_src.mkdir(parents=True)
    included = root / "frontend" / "README.md"
    included.parent.mkdir(parents=True)
    included.write_text("# Frontend one\n", encoding="utf-8")
    (docs_src / "frontend").mkdir()
    (docs_src / "frontend" / "README.md").write_text(
        '--8<-- "frontend/README.md"\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(serve, "ROOT", root)
    monkeypatch.setattr(serve, "DOCS_SRC", docs_src)
    monkeypatch.setattr(serve, "WATCH_PATHS", (docs_src,))

    first = serve.fingerprint()
    included.write_text("# Frontend two\n", encoding="utf-8")
    second = serve.fingerprint()

    assert first != second


def test_fingerprint_changes_when_non_markdown_snippet_include_changes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path
    docs_src = root / "docs" / "src"
    docs_src.mkdir(parents=True)
    included = root / "backend" / "src" / "example.py"
    included.parent.mkdir(parents=True)
    included.write_text("VALUE = 1\n", encoding="utf-8")
    (docs_src / "example.md").write_text(
        '--8<-- "backend/src/example.py"\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(serve, "ROOT", root)
    monkeypatch.setattr(serve, "DOCS_SRC", docs_src)
    monkeypatch.setattr(serve, "WATCH_PATHS", (docs_src,))

    assert serve.iter_files(included) == [included]

    first = serve.fingerprint()
    included.write_text("VALUE = 2\n", encoding="utf-8")
    second = serve.fingerprint()

    assert first != second


def test_fingerprint_changes_when_asset_changes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    src = tmp_path / "docs" / "src"
    assets = src / "assets"
    assets.mkdir(parents=True)
    logo = assets / "logo.png"
    logo.write_bytes(b"one")

    monkeypatch.setattr(serve, "ROOT", tmp_path)
    monkeypatch.setattr(serve, "DOCS_SRC", src)
    monkeypatch.setattr(serve, "WATCH_PATHS", (src,))

    first = serve.fingerprint()
    logo.write_bytes(b"two")
    second = serve.fingerprint()

    assert first != second
