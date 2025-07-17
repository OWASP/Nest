from unittest.mock import MagicMock, patch

from apps.sitemap.views import ProjectSitemap


class TestProjectSitemap:
    @patch("apps.sitemap.views.project.Project")
    def test_items(self, mock_project):
        mock_obj = MagicMock(is_indexable=True)
        mock_project.objects.filter.return_value = [mock_obj]
        sitemap = ProjectSitemap()

        assert list(sitemap.items()) == [mock_obj]

    def test_location(self):
        obj = MagicMock()
        obj.get_absolute_url.return_value = "/projects/foo"
        sitemap = ProjectSitemap()

        assert sitemap.location(obj) == "/projects/foo"
