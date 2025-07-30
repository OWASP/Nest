from unittest.mock import MagicMock, patch

from django.utils import timezone

from apps.sitemap.views.base import BaseSitemap
from apps.sitemap.views.organization import OrganizationSitemap


class TestOrganizationSitemap:
    def test_inherits_from_base(self):
        assert issubclass(OrganizationSitemap, BaseSitemap)

    def test_changefreq_returns_monthly(self):
        sitemap = OrganizationSitemap()
        mock_org = MagicMock()
        result = sitemap.changefreq(mock_org)

        assert result == "monthly"

    @patch("apps.sitemap.views.organization.Organization")
    def test_items_returns_filtered_queryset(self, mock_organization):
        mock_org1 = MagicMock()
        mock_org2 = MagicMock()

        mock_qs = MagicMock()
        mock_qs.order_by.return_value = [mock_org1, mock_org2]
        mock_organization.objects.filter.return_value = mock_qs

        sitemap = OrganizationSitemap()
        items = list(sitemap.items())

        mock_organization.objects.filter.assert_called_once_with(is_indexable=True)
        mock_qs.order_by.assert_called_once_with("-updated_at", "-created_at")
        assert items == [mock_org1, mock_org2]

    def test_location_returns_correct_url_format(self):
        """Test that location returns correctly formatted URL."""
        sitemap = OrganizationSitemap()
        mock_org = MagicMock()
        mock_org.login = "test-org"

        url = sitemap.location(mock_org)

        assert url == "/organizations/test-org"
        assert url.startswith("/organizations/")

    def test_lastmod_returns_updated_at(self):
        sitemap = OrganizationSitemap()
        updated_time = timezone.now()

        mock_org = MagicMock()
        mock_org.updated_at = updated_time

        result = sitemap.lastmod(mock_org)

        assert result == updated_time

    def test_priority_returns_valid_value(self):
        sitemap = OrganizationSitemap()
        mock_org = MagicMock()

        priority = sitemap.priority(mock_org)

        assert isinstance(priority, (int, float))
        assert 0.0 <= priority <= 1.0

    def test_change_frequency_attribute(self):
        sitemap = OrganizationSitemap()
        assert sitemap.change_frequency == "weekly"

    def test_prefix_attribute(self):
        sitemap = OrganizationSitemap()
        assert sitemap.prefix == "/organizations"
