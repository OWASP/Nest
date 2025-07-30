from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.sitemap.views.base import BaseSitemap
from apps.sitemap.views.organization import OrganizationSitemap


class TestOrganizationSitemap(TestCase):
    def setUp(self):
        self.sitemap = OrganizationSitemap()

    def test_inherits_from_base(self):
        self.assertTrue(issubclass(OrganizationSitemap, BaseSitemap))

    def test_changefreq_returns_weekly(self):
        mock_org = MagicMock()
        changefreq = self.sitemap.changefreq(mock_org)
        self.assertEqual(changefreq, "weekly")

    @patch("apps.sitemap.views.organization.Organization")
    def test_items_returns_only_indexable(self, mock_organization):
        mock_org1 = MagicMock(is_indexable=True)
        mock_org2 = MagicMock(is_indexable=True)

        mock_qs = MagicMock()
        mock_qs.order_by.return_value = [mock_org1, mock_org2]
        mock_organization.objects.filter.return_value = mock_qs

        items = list(self.sitemap.items())

        mock_organization.objects.filter.assert_called_once_with(is_indexable=True)
        mock_qs.order_by.assert_called_once_with("-updated_at", "-created_at")
        self.assertEqual(items, [mock_org1, mock_org2])

    def test_location_returns_correct_url_format(self):
        org = MagicMock(nest_key="test-org")
        url = self.sitemap.location(org)
        self.assertEqual(url, "/organizations/test-org")
