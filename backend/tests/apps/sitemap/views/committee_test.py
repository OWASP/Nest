from unittest.mock import MagicMock, patch

from django.utils import timezone

from apps.sitemap.views import CommitteeSitemap


class TestCommitteeSitemap:
    @patch("apps.sitemap.views.committee.Committee")
    def test_items(self, mock_committee):
        mock_obj = MagicMock(is_indexable=True)
        mock_committee.objects.filter.return_value = [mock_obj]
        sitemap = CommitteeSitemap()

        assert list(sitemap.items()) == [mock_obj]

    def test_location(self):
        sitemap = CommitteeSitemap()

        assert sitemap.location(MagicMock(nest_key="baz")) == "/committees/baz"

    def test_changefreq(self):
        sitemap = CommitteeSitemap()

        assert sitemap.changefreq(MagicMock()) == "weekly"

    def test_priority(self):
        sitemap = CommitteeSitemap()

        assert sitemap.priority(MagicMock()) == 0.8

    def test_lastmod(self):
        dt = timezone.now()
        obj = MagicMock(updated_at=dt, created_at=None)
        sitemap = CommitteeSitemap()

        assert sitemap.lastmod(obj) == dt

        obj = MagicMock(updated_at=None, created_at=dt)
        assert sitemap.lastmod(obj) == dt
