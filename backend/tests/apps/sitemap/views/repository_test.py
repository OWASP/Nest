import math
from unittest.mock import MagicMock, patch

from django.utils import timezone

from apps.sitemap.views.base import BaseSitemap
from apps.sitemap.views.repository import RepositorySitemap


class TestRepositorySitemap:
    def test_changefreq(self):
        sitemap = RepositorySitemap()

        assert sitemap.changefreq(MagicMock()) == "weekly"

    def test_inherits_from_base(self):
        assert issubclass(RepositorySitemap, BaseSitemap)

    @patch("apps.sitemap.views.repository.Repository")
    def test_items(self, mock_repository):
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset

        mock_obj = MagicMock(is_indexable=True)
        mock_queryset.__iter__ = lambda _: iter([mock_obj])

        mock_repository.objects.filter.return_value = mock_queryset

        sitemap = RepositorySitemap()

        result = list(sitemap.items())
        assert result == [mock_obj]

    def test_lastmod(self):
        dt = timezone.now()
        obj = MagicMock(updated_at=dt, created_at=None)
        sitemap = RepositorySitemap()

        assert sitemap.lastmod(obj) == dt

        obj = MagicMock(updated_at=None, created_at=dt)

        assert sitemap.lastmod(obj) == dt

    def test_limit(self):
        sitemap = RepositorySitemap()
        assert sitemap.limit == 50000

    def test_location(self):
        sitemap = RepositorySitemap()
        mock_organization = MagicMock(nest_key="test-org")
        mock_repository = MagicMock(key="test-repo", organization=mock_organization)

        assert (
            sitemap.location(mock_repository) == "/organizations/test-org/repositories/test-repo"
        )

    def test_priority(self):
        sitemap = RepositorySitemap()

        assert math.isclose(sitemap.priority(MagicMock()), 0.7)
