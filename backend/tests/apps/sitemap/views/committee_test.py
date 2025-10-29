from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from apps.sitemap.views.base import BaseSitemap
from apps.sitemap.views.committee import CommitteeSitemap


class TestCommitteeSitemap:
    def test_changefreq(self):
        sitemap = CommitteeSitemap()

        assert sitemap.changefreq(MagicMock()) == "monthly"

    def test_inherits_from_base(self):
        assert issubclass(CommitteeSitemap, BaseSitemap)

    @patch("apps.sitemap.views.committee.Committee")
    def test_items(self, mock_committee):
        mock_obj = MagicMock(is_indexable=True)
        mock_qs = MagicMock()
        mock_qs.order_by.return_value = [mock_obj]
        mock_committee.active_committees = mock_qs
        sitemap = CommitteeSitemap()

        assert list(sitemap.items()) == [mock_obj]

    def test_lastmod(self):
        dt = timezone.now()
        obj = MagicMock(updated_at=dt, created_at=None)
        sitemap = CommitteeSitemap()

        assert sitemap.lastmod(obj) == dt

        obj = MagicMock(updated_at=None, created_at=dt)
        assert sitemap.lastmod(obj) == dt

    def test_limit(self):
        sitemap = CommitteeSitemap()
        assert sitemap.limit == 50000

    def test_location(self):
        sitemap = CommitteeSitemap()

        assert sitemap.location(MagicMock(nest_key="baz")) == "/committees/baz"

    def test_priority(self):
        sitemap = CommitteeSitemap()

        assert pytest.approx(sitemap.priority(MagicMock())) == 0.8
