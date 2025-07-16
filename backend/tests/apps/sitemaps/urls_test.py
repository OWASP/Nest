import unittest
from unittest.mock import MagicMock, patch

from apps.sitemaps import urls as sm_urls


class TestSitemapUrls(unittest.TestCase):
    @patch("apps.sitemaps.urls.cached_sitemap_view")
    def test_urlpatterns_registered(self, mock_cached_sitemap_view):
        dummy_view = MagicMock()
        mock_cached_sitemap_view.return_value = dummy_view
        import importlib
        import sys

        if "apps.sitemaps.urls" in sys.modules:
            importlib.reload(sm_urls)
        expected_names = [
            "sitemap-index",
            "sitemap-chapters",
            "sitemap-committees",
            "sitemap-projects",
            "sitemap-static",
            "sitemap-users",
        ]
        found_names = [p.name for p in sm_urls.urlpatterns]
        for name in expected_names:
            assert name in found_names
