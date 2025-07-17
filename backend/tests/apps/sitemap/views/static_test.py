from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.sitemap.views import StaticSitemap


@pytest.fixture
def sitemap():
    return StaticSitemap()


class TestStaticSitemap:
    @patch("apps.sitemap.views.static.Chapter.objects.aggregate")
    @patch("apps.sitemap.views.static.Committee.objects.aggregate")
    @patch("apps.sitemap.views.static.Project.objects.aggregate")
    @patch("apps.sitemap.views.static.User.objects.aggregate")
    def test_lastmod(self, mock_user, mock_project, mock_committee, mock_chapter, sitemap):
        dt = timezone.now()
        mock_chapter.return_value = {"latest": dt}
        mock_committee.return_value = {"latest": dt}
        mock_project.return_value = {"latest": dt}
        mock_user.return_value = {"latest": dt}
        for item in sitemap.STATIC_ROUTES:
            result = sitemap.lastmod(item)
            assert result is not None

    def test_items(self, sitemap):
        assert sitemap.items() == sitemap.STATIC_ROUTES

    def test_location(self, sitemap):
        for item in sitemap.STATIC_ROUTES:
            assert sitemap.location(item) == item["path"]

    def test_changefreq(self, sitemap):
        for item in sitemap.STATIC_ROUTES:
            assert sitemap.changefreq(item) == item["changefreq"]

    def test_priority(self, sitemap):
        for item in sitemap.STATIC_ROUTES:
            assert sitemap.priority(item) == item["priority"]
