import math
from unittest.mock import MagicMock, patch

import pytest
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
        mock_obj = MagicMock()
        # Create a mock queryset that properly chains the methods
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value.order_by.return_value = [mock_obj]
        mock_repository.objects = mock_queryset
        sitemap = RepositorySitemap()

        result = list(sitemap.items())
        assert result == [mock_obj]
        
        # Verify the correct methods were called with correct arguments
        mock_queryset.filter.assert_called_once_with(
            is_archived=False,
            owner__isnull=False,
        )
        mock_queryset.filter.return_value.order_by.assert_called_once_with(
            "-updated_at",
            "-created_at",
        )

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
        mock_owner = MagicMock(login="test-org")
        mock_repo = MagicMock(key="test-repo", owner=mock_owner)

        assert sitemap.location(mock_repo) == "/organizations/test-org/repositories/test-repo"

    def test_location_raises_error_for_repository_without_owner(self):
        sitemap = RepositorySitemap()
        mock_repo = MagicMock(owner=None)
        mock_repo.name = "test-repo"

        with pytest.raises(ValueError, match="Repository 'test-repo' has no owner"):
            sitemap.location(mock_repo)

    def test_priority(self):
        sitemap = RepositorySitemap()

        assert math.isclose(sitemap.priority(MagicMock()), 0.7)