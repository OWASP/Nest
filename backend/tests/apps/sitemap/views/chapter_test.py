import math
from unittest.mock import MagicMock, patch

from django.utils import timezone

from apps.sitemap.views import ChapterSitemap


class TestChapterSitemap:
    @patch("apps.sitemap.views.chapter.Chapter")
    def test_items(self, mock_chapter):
        mock_obj = MagicMock(is_indexable=True)
        mock_chapter.objects.filter.return_value = [mock_obj]
        sitemap = ChapterSitemap()

        assert list(sitemap.items()) == [mock_obj]

    def test_location(self):
        sitemap = ChapterSitemap()

        assert sitemap.location(MagicMock(nest_key="bar")) == "/chapters/bar"

    def test_changefreq(self):
        obj = MagicMock()
        sitemap = ChapterSitemap()

        assert sitemap.changefreq(obj) == "weekly"

    def test_priority(self):
        obj = MagicMock()
        sitemap = ChapterSitemap()

        assert math.isclose(sitemap.priority(obj), 0.8)

    def test_lastmod(self):
        dt = timezone.now()
        obj = MagicMock(updated_at=dt, created_at=None)
        sitemap = ChapterSitemap()

        assert sitemap.lastmod(obj) == dt

        obj = MagicMock(updated_at=None, created_at=dt)

        assert sitemap.lastmod(obj) == dt
