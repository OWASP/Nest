"""Build the real documentation configuration against compatibility fixtures."""

from __future__ import annotations

import json
import re
import subprocess
import tomllib
from pathlib import Path

import pytest

import serve

CONFIG_PATH = serve.ROOT / serve.CONFIG_FILE


def toml_key(key: str) -> str:
    """Return a TOML key, quoting it when it is not a bare key."""
    return key if re.fullmatch(r"[A-Za-z0-9_-]+", key) else json.dumps(key)


def toml_value(value: object) -> str:
    """Return a TOML value for the reduced compatibility configuration."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(toml_value(item) for item in value) + "]"
    if isinstance(value, dict):
        fields = ", ".join(f"{toml_key(key)} = {toml_value(item)}" for key, item in value.items())
        return "{" + fields + "}"

    message = f"Unsupported configuration value: {type(value).__name__}"
    raise TypeError(message)


def write_project_config(path: Path, project: dict[str, object]) -> None:
    """Write a Zensical project table."""
    lines = ["[project]"]
    lines.extend(f"{toml_key(key)} = {toml_value(value)}" for key, value in project.items())
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


@pytest.fixture(scope="module")
def built_site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build a small site using the shared production configuration."""
    root = tmp_path_factory.mktemp("zensical")
    docs = root / "docs"
    docs.mkdir()

    with CONFIG_PATH.open("rb") as handle:
        project = tomllib.load(handle)["project"]
    project.update(docs_dir="docs", site_dir="site", nav=[{"Home": "index.md"}], extra_css=[])
    project["theme"].pop("custom_dir", None)
    project["theme"].pop("logo", None)
    project["theme"].pop("favicon", None)
    project["theme"]["font"] = False
    # Keep network downloads out of this compatibility fixture.
    project["plugins"].setdefault("privacy", {})["assets"] = False
    write_project_config(root / serve.CONFIG_FILE, project)
    (root / "included.md").write_text("Included README content.\n", encoding="utf-8")
    (root / "README.md").write_text(
        "README introduction excluded from docs.\n\n"
        "<!-- --8<-- [start:docs] -->\n"
        "Included README docs section.\n"
        "<!-- --8<-- [end:docs] -->\n\n"
        "README footer excluded from docs.\n",
        encoding="utf-8",
    )
    (docs / "index.md").write_text(
        "---\ntags:\n  - Compatibility\n---\n\n"
        "# Documentation compatibility\n\n"
        '--8<-- "included.md"\n\n'
        '--8<-- "README.md:docs"\n\n'
        "```mermaid\nflowchart LR\n  Markdown --> Website\n```\n\n"
        "<!-- material/tags -->\n",
        encoding="utf-8",
    )

    result = subprocess.run(  # noqa: S603
        ["zensical", "build", "--strict", "--config-file", serve.CONFIG_FILE],  # noqa: S607
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return root / "site"


class TestMermaidRendering:
    """Tests for Mermaid fences in the built site."""

    def test_diagram_instead_of_highlighted_code_block(self, built_site: Path) -> None:
        """Keep Mermaid fences available for client-side diagram rendering."""
        html = (built_site / "index.html").read_text(encoding="utf-8")

        assert re.search(r'<(?:div|pre)\b[^>]*class=["\']?mermaid\b', html)
        assert "flowchart LR" in html
        assert "Markdown --&gt; Website" in html or "Markdown --> Website" in html


class TestReadmeIncludes:
    """Tests for snippet includes copied into the built site."""

    def test_includes_are_rendered(self, built_site: Path) -> None:
        """Expand included files."""
        html = (built_site / "index.html").read_text(encoding="utf-8")

        assert "Included README content." in html
        assert "--8&lt;--" not in html

    def test_only_named_docs_section_is_included(self, built_site: Path) -> None:
        """Include the marked docs section without surrounding README content."""
        html = (built_site / "index.html").read_text(encoding="utf-8")

        assert "Included README docs section." in html
        assert "README introduction excluded from docs." not in html
        assert "README footer excluded from docs." not in html


class TestTagsAndSearch:
    """Tests for plugins that remain enabled in the reduced build."""

    def test_remain_enabled(self, built_site: Path) -> None:
        """Retain tag links and the search component in generated HTML."""
        html = (built_site / "index.html").read_text(encoding="utf-8")

        assert "Compatibility" in html
        assert "md-tag" in html
        assert 'data-md-component="search"' in html or "data-md-component=search" in html
