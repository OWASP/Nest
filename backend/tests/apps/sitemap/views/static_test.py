import math
from unittest.mock import ANY, patch

import pytest
from django.utils import timezone

from apps.sitemap.views.base import BaseSitemap
from apps.sitemap.views.static import StaticSitemap


@pytest.fixture
def sitemap():
    return StaticSitemap()


class TestStaticSitemap:
    def test_changefreq(self, sitemap):
        for item in sitemap.STATIC_ROUTES:
            assert sitemap.changefreq(item) == item["changefreq"]

    def test_inherits_from_base(self):
        assert issubclass(StaticSitemap, BaseSitemap)

    def test_items(self, sitemap):
        assert sitemap.items() == sitemap.STATIC_ROUTES

    @patch("apps.sitemap.views.static.Chapter.objects.aggregate")
    @patch("apps.sitemap.views.static.Committee.objects.aggregate")
    @patch("apps.sitemap.views.static.Organization.objects.aggregate")
    @patch("apps.sitemap.views.static.Snapshot.objects.aggregate")
    @patch("apps.sitemap.views.static.Project.objects.aggregate")
    @patch("apps.sitemap.views.static.User.objects.aggregate")
    def test_lastmod(
        self,
        mock_user,
        mock_project,
        mock_organization,
        mock_committee,
        mock_chapter,
        sitemap,
    ):
        dt = timezone.now()
        mock_chapter.return_value = {"latest": dt}
        mock_committee.return_value = {"latest": dt}
        mock_organization.return_value = {"latest": dt}
        mock_project.return_value = {"latest": dt}
        mock_user.return_value = {"latest": dt}

        for item in sitemap.STATIC_ROUTES:
            result = sitemap.lastmod(item)
            assert result is not None

    def test_lastmod_unmapped_path_returns_current_time(self, sitemap):
        """Test lastmod returns current time for paths not in path_to_model."""
        from datetime import UTC, datetime as dt
        from unittest.mock import Mock
        
        current_time = dt.now(UTC)
        mock_datetime = Mock()
        mock_datetime.now.return_value = current_time
        
        with patch("apps.sitemap.views.static.datetime", mock_datetime):
            # Test with a path that's not in the path_to_model mapping
            item = {"path": "/unknown-path"}
            result = sitemap.lastmod(item)

            assert result == current_time
            mock_datetime.now.assert_called_once_with(UTC)

    @patch("apps.sitemap.views.static.Project.objects.aggregate")
    def test_lastmod_with_mapped_path(self, mock_aggregate, sitemap):
        """Test lastmod uses model's latest updated_at for mapped paths."""
        dt = timezone.now()
        mock_aggregate.return_value = {"latest": dt}

        item = {"path": "/projects"}
        result = sitemap.lastmod(item)

        mock_aggregate.assert_called_once_with(latest=ANY)
        assert result == dt

    def test_limit(self, sitemap):
        assert sitemap.limit == 50000

    def test_location(self, sitemap):
        for item in sitemap.STATIC_ROUTES:
            assert sitemap.location(item) == item["path"]

    def test_priority(self, sitemap):
        for item in sitemap.STATIC_ROUTES:
            assert math.isclose(sitemap.priority(item), item["priority"])
