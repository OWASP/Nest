"""Verify the production theme and privacy output without reducing its configuration."""

from __future__ import annotations

import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from serve import CONFIG_FILE, ROOT, snippet_include_paths

pytestmark = pytest.mark.network


class RenderedPage(HTMLParser):
    """Collect theme classes and assets independently of HTML minification."""

    def __init__(self, html: str) -> None:
        """Read the rendered page's classes, images, stylesheets, and icons."""
        super().__init__()
        self.classes: set[str] = set()
        self.images: set[str] = set()
        self.stylesheets: set[str] = set()
        self.icons: set[str] = set()
        self.feed(html)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Collect the attributes used by the production output checks."""
        attributes = dict(attrs)
        self.classes.update((attributes.get("class") or "").split())
        if tag == "img" and attributes.get("src"):
            self.images.add(attributes["src"])
        elif tag == "link" and attributes.get("href"):
            if attributes.get("rel") == "stylesheet":
                self.stylesheets.add(attributes["href"])
            elif attributes.get("rel") == "icon":
                self.icons.add(attributes["href"])


def local_asset(page: Path, reference: str, site: Path) -> Path:
    """Require an asset reference to resolve to a nonempty file within the site."""
    url = urlsplit(reference)
    assert not url.scheme, f"Asset was not made local: {reference}"
    assert not url.netloc, f"Asset was not made local: {reference}"
    asset = (page.parent / url.path).resolve()
    assert asset.is_relative_to(site.resolve()), reference
    assert asset.is_file(), f"Missing asset: {asset}"
    assert asset.stat().st_size, f"Empty asset: {asset}"
    return asset


@pytest.fixture(scope="module")
def production_site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build the real documentation using the unmodified production configuration."""
    root = tmp_path_factory.mktemp("production-docs")
    shutil.copy2(ROOT / CONFIG_FILE, root / CONFIG_FILE)
    for directory in ("docs/src", "docs/overrides"):
        shutil.copytree(ROOT / directory, root / directory)
    for include in snippet_include_paths():
        target = root / include.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(include, target)

    result = subprocess.run(  # noqa: S603
        ["zensical", "build", "--strict", "--config-file", CONFIG_FILE],  # noqa: S607
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return root / "site"


class TestProductionTemplates:
    """Tests for Nest branding and local asset links in production HTML."""

    @pytest.mark.parametrize("page_path", ["index.html", "backend/index.html"])
    def test_templates_and_assets(self, production_site: Path, page_path: str) -> None:
        """Preserve Nest branding and asset links on the homepage and a nested page."""
        page = production_site / page_path
        rendered = RenderedPage(page.read_text(encoding="utf-8"))
        assert {
            "nest-header__site-name",
            "nest-header__docs-icon",
            "nest-footer",
            "nest-footer__logos",
        } <= rendered.classes

        assets = {
            "assets/images/logo.png": rendered.images,
            "assets/images/owasp-logo.svg": rendered.images,
            "assets/images/favicon.png": rendered.icons,
            "assets/stylesheets/nest-theme.css": rendered.stylesheets,
        }
        for path, references in assets.items():
            expected = production_site / path
            matching = [
                reference for reference in references if urlsplit(reference).path.endswith(path)
            ]
            assert matching, f"Production asset is not linked from {page_path}: {path}"
            assert all(
                local_asset(page, reference, production_site) == expected for reference in matching
            )
            assert expected.read_bytes() == (ROOT / "docs/src" / path).read_bytes()


class TestProductionPrivacy:
    """Tests for privacy-plugin downloads of configured fonts."""

    def test_downloads_fonts_locally(self, production_site: Path) -> None:
        """Keep both configured fonts and all their stylesheet references local."""
        page = production_site / "index.html"
        rendered = RenderedPage(page.read_text(encoding="utf-8"))
        fonts = [
            reference
            for reference in rendered.stylesheets
            if urlsplit(reference).path.startswith("assets/external/fonts.googleapis.com/")
        ]
        assert fonts, "The configured font stylesheet is missing"
        for reference in fonts:
            stylesheet = local_asset(page, reference, production_site)
            css = stylesheet.read_text(encoding="utf-8")
            families = re.findall(r"font-family:\s*['\"]([^'\"]+)['\"]", css)
            assert {"Geist", "Geist Mono"} <= set(families)
            font_urls = re.findall(r"url\(([^)]+)\)", css)
            assert font_urls, "The font stylesheet has no font files"
            for font_url in font_urls:
                local_asset(stylesheet, font_url.strip().strip("\"'"), production_site)
