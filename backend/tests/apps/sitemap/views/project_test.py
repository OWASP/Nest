from unittest.mock import MagicMock, patch

from apps.sitemap.views.base import BaseSitemap
from apps.sitemap.views.project import ProjectSitemap


class TestProjectSitemap:
    def test_changefreq(self):
        sitemap = ProjectSitemap()

        assert sitemap.changefreq(MagicMock()) == "weekly"

    def test_inherits_from_base(self):
        assert issubclass(ProjectSitemap, BaseSitemap)

    @patch("apps.sitemap.views.project.Project")
    def test_items(self, mock_project):
        mock_obj = MagicMock(is_indexable=True)
        mock_qs = MagicMock()
        mock_qs.order_by.return_value = [mock_obj]
        mock_project.active_projects = mock_qs
        sitemap = ProjectSitemap()

        assert list(sitemap.items()) == [mock_obj]

    def test_limit(self):
        sitemap = ProjectSitemap()
        assert sitemap.limit == 50000

    def test_location(self):
        sitemap = ProjectSitemap()

        assert sitemap.location(MagicMock(nest_key="bar")) == "/projects/bar"
