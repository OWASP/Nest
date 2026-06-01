import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from apps.sitemap import urls as sitemap_urls


class TestSitemapUrls(unittest.TestCase):
    @patch("apps.sitemap.urls.cached_sitemap_view")
    def test_urlpatterns_registered(self, mock_cached_sitemap_view):
        dummy_view = MagicMock()
        mock_cached_sitemap_view.return_value = dummy_view

        # If the module was already imported, reload it to ensure patches take effect.
        # This is necessary because Django's URL resolver may cache the module, and
        # patching after import would not affect already-imported symbols.
        if "apps.sitemap.urls" in sys.modules:
            importlib.reload(sitemap_urls)

        expected_paths = (
            "sitemap.xml",
            "sitemap/chapters.xml",
            "sitemap/committees.xml",
            "sitemap/members.xml",
            "sitemap/organizations.xml",
            "sitemap/snapshots.xml",
            "sitemap/projects.xml",
            "sitemap/repositories.xml",
            "sitemap/static.xml",
        )
        found_paths = {p.pattern._route for p in sitemap_urls.urlpatterns}
        for path in expected_paths:
            assert path in found_paths
