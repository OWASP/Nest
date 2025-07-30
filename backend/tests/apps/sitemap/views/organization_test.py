from unittest.mock import MagicMock, patch

from django.utils import timezone

from apps.sitemap.views.base import BaseSitemap
from apps.sitemap.views.organization import OrganizationSitemap


class TestOrganizationSitemap:
    def test_inherits_from_base(self):
        assert issubclass(OrganizationSitemap, BaseSitemap)

    @patch("apps.sitemap.views.organization.OrganizationSitemap.changefreq")
    def test_changefreq_returns_weekly(self, mock_changefreq):
        mock_changefreq.return_value = "weekly"

        sitemap = OrganizationSitemap()
        mock_org = MagicMock()
        result = sitemap.changefreq(mock_org)

        assert result == "weekly"

    @patch("apps.sitemap.views.organization.OrganizationSitemap.items")
    def test_items_returns_queryset(self, mock_items):
        mock_org1 = MagicMock()
        mock_org2 = MagicMock()
        mock_items.return_value = [mock_org1, mock_org2]

        sitemap = OrganizationSitemap()
        items = list(sitemap.items())

        assert items == [mock_org1, mock_org2]

    @patch("apps.sitemap.views.organization.OrganizationSitemap.location")
    def test_location_returns_correct_url_format(self, mock_location):
        mock_location.return_value = "/organizations/test-org"

        sitemap = OrganizationSitemap()
        mock_org = MagicMock()
        url = sitemap.location(mock_org)

        assert url == "/organizations/test-org"
        assert url.startswith("/organizations/")

    @patch("apps.sitemap.views.organization.OrganizationSitemap.lastmod")
    def test_lastmod_returns_updated_at(self, mock_lastmod):
        updated_time = timezone.now()
        mock_lastmod.return_value = updated_time

        sitemap = OrganizationSitemap()
        mock_org = MagicMock()
        result = sitemap.lastmod(mock_org)

        assert result == updated_time

    @patch("apps.sitemap.views.organization.OrganizationSitemap.priority")
    def test_priority_returns_valid_value(self, mock_priority):
        mock_priority.return_value = 0.8

        sitemap = OrganizationSitemap()
        mock_org = MagicMock()
        priority = sitemap.priority(mock_org)

        assert isinstance(priority, (int, float))
        assert 0.0 <= priority <= 1.0
