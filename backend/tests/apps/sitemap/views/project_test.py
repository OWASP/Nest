from unittest.mock import MagicMock, patch

from apps.sitemap.views.base import BaseSitemap
from apps.sitemap.views.project import ProjectSitemap


class TestProjectSitemap:
    @patch("apps.sitemap.views.project.Project")
    def test_items(self, mock_project):
        mock_obj = MagicMock(is_indexable=True)
        mock_project.objects.filter.return_value = [mock_obj]
        sitemap = ProjectSitemap()

        assert list(sitemap.items()) == [mock_obj]

    def test_location(self):
        sitemap = ProjectSitemap()

        assert sitemap.location(MagicMock(nest_key="bar")) == "/projects/bar"

    def test_inherits_from_base(self):
        assert issubclass(ProjectSitemap, BaseSitemap)
