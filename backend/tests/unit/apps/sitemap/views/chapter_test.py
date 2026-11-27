import math
from unittest.mock import MagicMock, patch

from django.utils import timezone

from apps.sitemap.views.base import BaseSitemap
from apps.sitemap.views.chapter import ChapterSitemap


class TestChapterSitemap:
    def test_changefreq(self):
        obj = MagicMock()
        sitemap = ChapterSitemap()

        assert sitemap.changefreq(obj) == "weekly"

    def test_inherits_from_base(self):
        assert issubclass(ChapterSitemap, BaseSitemap)

    @patch("apps.sitemap.views.chapter.Chapter")
    def test_items(self, mock_chapter):
        mock_obj = MagicMock(is_indexable=True)
        mock_qs = MagicMock()
        mock_qs.order_by.return_value = [mock_obj]
        mock_chapter.active_chapters = mock_qs
        sitemap = ChapterSitemap()

        assert list(sitemap.items()) == [mock_obj]

    def test_lastmod(self):
        dt = timezone.now()
        obj = MagicMock(updated_at=dt, created_at=None)
        sitemap = ChapterSitemap()

        assert sitemap.lastmod(obj) == dt

        obj = MagicMock(updated_at=None, created_at=dt)

        assert sitemap.lastmod(obj) == dt

    def test_limit(self):
        sitemap = ChapterSitemap()
        assert sitemap.limit == 50000

    def test_location(self):
        sitemap = ChapterSitemap()

        assert sitemap.location(MagicMock(nest_key="bar")) == "/chapters/bar"

    def test_priority(self):
        obj = MagicMock()
        sitemap = ChapterSitemap()

        assert math.isclose(sitemap.priority(obj), 0.8)
