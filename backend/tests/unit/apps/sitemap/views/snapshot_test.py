from unittest.mock import MagicMock, patch

from apps.sitemap.views.base import BaseSitemap
from apps.sitemap.views.snapshot import SnapshotSitemap


class TestSnapshotSitemap:
    def test_changefreq(self):
        sitemap = SnapshotSitemap()

        assert sitemap.changefreq(MagicMock()) == "monthly"

    def test_inherits_from_base(self):
        assert issubclass(SnapshotSitemap, BaseSitemap)

    @patch("apps.sitemap.views.snapshot.Snapshot")
    def test_items(self, mock_snapshot):
        mock_obj = MagicMock(_indexable=True)
        mock_snapshot.objects.filter.return_value.order_by.return_value = [mock_obj]
        mock_snapshot.Status.COMPLETED = "completed"
        sitemap = SnapshotSitemap()

        assert list(sitemap.items()) == [mock_obj]

    def test_limit(self):
        sitemap = SnapshotSitemap()
        assert sitemap.limit == 50000

    def test_location(self):
        sitemap = SnapshotSitemap()

        assert sitemap.location(MagicMock(key="bar")) == "/snapshots/bar"
