from unittest.mock import MagicMock, patch

import pytest

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
        mock_qs = MagicMock()
        mock_qs.filter.return_value.order_by.return_value.__getitem__.return_value = [mock_obj]
        mock_repository.objects = mock_qs
        sitemap = RepositorySitemap()

        assert list(sitemap.items()) == [mock_obj]

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
        mock_repo = MagicMock(name="test-repo", owner=None)

        with pytest.raises(ValueError, match="Repository 'test-repo' has no owner"):
            sitemap.location(mock_repo)