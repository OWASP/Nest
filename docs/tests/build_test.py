"""Build the real documentation configuration against compatibility fixtures."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
import yaml

CONFIG_PATH = Path(__file__).resolve().parents[2] / ".mkdocs.yaml"


@pytest.fixture(scope="module")
def built_site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("zensical")
    docs = root / "docs"
    docs.mkdir()

    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    config.update(docs_dir="docs", site_dir="site", nav=[{"Home": "index.md"}], extra_css=[])
    config["theme"].pop("custom_dir", None)
    config["theme"].pop("logo", None)
    config["theme"].pop("favicon", None)
    config["theme"]["font"] = False
    # Keep network downloads out of this compatibility fixture.
    config["plugins"] = [
        {"privacy": {"assets": False}} if plugin == "privacy" else plugin
        for plugin in config["plugins"]
    ]
    (root / ".mkdocs.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")
    (root / "included.md").write_text("Included README content.\n", encoding="utf-8")
    (root / "README.md").write_text(
        "README introduction excluded from docs.\n\n"
        "<!-- --8<-- [start:docs] -->\n"
        "Included README docs section.\n"
        "<!-- --8<-- [end:docs] -->\n\n"
        "README footer excluded from docs.\n",
        encoding="utf-8",
    )
    (root / "example.py").write_text(
        'def answer() -> int:\n    """Return the documented answer."""\n    return 42\n',
        encoding="utf-8",
    )
    (docs / "index.md").write_text(
        "---\ntags:\n  - Compatibility\n---\n\n"
        "# Documentation compatibility\n\n"
        '--8<-- "included.md"\n\n'
        '--8<-- "README.md:docs"\n\n'
        "```mermaid\nflowchart LR\n  Markdown --> Website\n```\n\n"
        "::: example.answer\n\n"
        "<!-- material/tags -->\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["zensical", "build", "--strict", "--config-file", ".mkdocs.yaml"],  # noqa: S607
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return root / "site"


def test_mermaid_is_a_diagram_instead_of_a_highlighted_code_block(built_site: Path) -> None:
    html = (built_site / "index.html").read_text(encoding="utf-8")

    assert re.search(r'<(?:div|pre)\b[^>]*class=["\']?mermaid\b', html)
    assert "flowchart LR" in html
    assert "Markdown --&gt; Website" in html or "Markdown --> Website" in html


def test_readme_includes_and_python_api_documentation_are_rendered(built_site: Path) -> None:
    html = (built_site / "index.html").read_text(encoding="utf-8")

    assert "Included README content." in html
    assert "Return the documented answer." in html
    assert "example.answer" in html
    assert "--8&lt;--" not in html


def test_only_the_named_readme_docs_section_is_included(built_site: Path) -> None:
    html = (built_site / "index.html").read_text(encoding="utf-8")

    assert "Included README docs section." in html
    assert "README introduction excluded from docs." not in html
    assert "README footer excluded from docs." not in html


def test_tags_and_search_remain_enabled(built_site: Path) -> None:
    html = (built_site / "index.html").read_text(encoding="utf-8")

    assert "Compatibility" in html
    assert "md-tag" in html
    assert 'data-md-component="search"' in html or "data-md-component=search" in html
