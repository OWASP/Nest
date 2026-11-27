from unittest.mock import MagicMock, patch

from apps.sitemap.views.base import BaseSitemap
from apps.sitemap.views.organization import OrganizationSitemap


class TestOrganizationSitemap:
    def test_changefreq(self):
        sitemap = OrganizationSitemap()

        assert sitemap.changefreq(MagicMock()) == "monthly"

    def test_inherits_from_base(self):
        assert issubclass(OrganizationSitemap, BaseSitemap)

    @patch("apps.sitemap.views.organization.Organization")
    def test_items(self, mock_organization):
        mock_obj = MagicMock(is_indexable=True)
        mock_queryset = MagicMock()
        mock_queryset.__iter__ = lambda _: iter([mock_obj])
        mock_organization.related_organizations.order_by.return_value = mock_queryset
        sitemap = OrganizationSitemap()

        assert list(sitemap.items()) == [mock_obj]

    def test_limit(self):
        sitemap = OrganizationSitemap()

        assert sitemap.limit == 50000

    def test_location(self):
        sitemap = OrganizationSitemap()

        assert sitemap.location(MagicMock(nest_key="bar")) == "/organizations/bar"
