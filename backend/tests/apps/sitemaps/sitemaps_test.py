import unittest
from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory
from django.utils import timezone

from apps.sitemaps import sitemaps as sm


class TestStaticSitemap(unittest.TestCase):
    def setUp(self):
        self.sitemap = sm.StaticSitemap()

    @patch("apps.sitemaps.sitemaps.Chapter.objects.aggregate")
    @patch("apps.sitemaps.sitemaps.Committee.objects.aggregate")
    @patch("apps.sitemaps.sitemaps.Project.objects.aggregate")
    @patch("apps.sitemaps.sitemaps.User.objects.aggregate")
    def test_lastmod(self, mock_user, mock_project, mock_committee, mock_chapter):
        dt = timezone.now()
        mock_chapter.return_value = {"latest": dt}
        mock_committee.return_value = {"latest": dt}
        mock_project.return_value = {"latest": dt}
        mock_user.return_value = {"latest": dt}
        for item in sm.STATIC_ROUTES:
            result = self.sitemap.lastmod(item)
            assert result is not None

    def test_items(self):
        assert self.sitemap.items() == sm.STATIC_ROUTES

    def test_location(self):
        for item in sm.STATIC_ROUTES:
            assert self.sitemap.location(item) == item["path"]

    def test_changefreq(self):
        for item in sm.STATIC_ROUTES:
            assert self.sitemap.changefreq(item) == item["changefreq"]

    def test_priority(self):
        for item in sm.STATIC_ROUTES:
            assert self.sitemap.priority(item) == item["priority"]


class TestGetStaticPriority(unittest.TestCase):
    def test_priority_for_known_path(self):
        assert abs(sm.get_static_priority("/projects") - 0.9) < 1e-7
        assert abs(sm.get_static_priority("/chapters") - 0.8) < 1e-7

    def test_priority_for_unknown_path(self):
        assert abs(sm.get_static_priority("/unknown") - 0.7) < 1e-7


class TestProjectSitemap(unittest.TestCase):
    @patch("apps.sitemaps.sitemaps.Project")
    def test_items(self, mock_project):
        mock_obj = MagicMock(is_indexable=True)
        mock_project.objects.filter.return_value = [mock_obj]
        sitemap = sm.ProjectSitemap()
        assert list(sitemap.items()) == [mock_obj]

    def test_location(self):
        obj = MagicMock(nest_key="foo")
        sitemap = sm.ProjectSitemap()
        assert sitemap.location(obj) == "/projects/foo"

    def test_changefreq(self):
        obj = MagicMock()
        sitemap = sm.ProjectSitemap()
        assert sitemap.changefreq(obj) == "weekly"

    def test_priority(self):
        obj = MagicMock()
        sitemap = sm.ProjectSitemap()
        assert sitemap.priority(obj) == sm.get_static_priority("/projects")

    def test_lastmod(self):
        dt = timezone.now()
        obj = MagicMock(updated_at=dt, created_at=None)
        sitemap = sm.ProjectSitemap()
        assert sitemap.lastmod(obj) == dt
        obj = MagicMock(updated_at=None, created_at=dt)
        assert sitemap.lastmod(obj) == dt


class TestChapterSitemap(unittest.TestCase):
    @patch("apps.sitemaps.sitemaps.Chapter")
    def test_items(self, mock_chapter):
        mock_obj = MagicMock(is_indexable=True)
        mock_chapter.objects.filter.return_value = [mock_obj]
        sitemap = sm.ChapterSitemap()
        assert list(sitemap.items()) == [mock_obj]

    def test_location(self):
        obj = MagicMock(nest_key="bar")
        sitemap = sm.ChapterSitemap()
        assert sitemap.location(obj) == "/chapters/bar"

    def test_changefreq(self):
        obj = MagicMock()
        sitemap = sm.ChapterSitemap()
        assert sitemap.changefreq(obj) == "weekly"

    def test_priority(self):
        obj = MagicMock()
        sitemap = sm.ChapterSitemap()
        assert sitemap.priority(obj) == sm.get_static_priority("/chapters")

    def test_lastmod(self):
        dt = timezone.now()
        obj = MagicMock(updated_at=dt, created_at=None)
        sitemap = sm.ChapterSitemap()
        assert sitemap.lastmod(obj) == dt
        obj = MagicMock(updated_at=None, created_at=dt)
        assert sitemap.lastmod(obj) == dt


class TestCommitteeSitemap(unittest.TestCase):
    @patch("apps.sitemaps.sitemaps.Committee")
    def test_items(self, mock_committee):
        mock_obj = MagicMock(is_indexable=True)
        mock_committee.objects.filter.return_value = [mock_obj]
        sitemap = sm.CommitteeSitemap()
        assert list(sitemap.items()) == [mock_obj]

    def test_location(self):
        obj = MagicMock(nest_key="baz")
        sitemap = sm.CommitteeSitemap()
        assert sitemap.location(obj) == "/committees/baz"

    def test_changefreq(self):
        obj = MagicMock()
        sitemap = sm.CommitteeSitemap()
        assert sitemap.changefreq(obj) == "weekly"

    def test_priority(self):
        obj = MagicMock()
        sitemap = sm.CommitteeSitemap()
        assert sitemap.priority(obj) == sm.get_static_priority("/committees")

    def test_lastmod(self):
        dt = timezone.now()
        obj = MagicMock(updated_at=dt, created_at=None)
        sitemap = sm.CommitteeSitemap()
        assert sitemap.lastmod(obj) == dt
        obj = MagicMock(updated_at=None, created_at=dt)
        assert sitemap.lastmod(obj) == dt


class TestUserSitemap(unittest.TestCase):
    @patch("apps.sitemaps.sitemaps.User")
    def test_items(self, mock_user):
        mock_obj = MagicMock(is_indexable=True)
        mock_user.objects.filter.return_value = [mock_obj]
        sitemap = sm.UserSitemap()
        assert list(sitemap.items()) == [mock_obj]

    def test_location(self):
        obj = MagicMock(login="qux")
        sitemap = sm.UserSitemap()
        assert sitemap.location(obj) == "/members/qux"

    def test_changefreq(self):
        obj = MagicMock()
        sitemap = sm.UserSitemap()
        assert sitemap.changefreq(obj) == "weekly"

    def test_priority(self):
        obj = MagicMock()
        sitemap = sm.UserSitemap()
        assert sitemap.priority(obj) == sm.get_static_priority("/members")

    def test_lastmod(self):
        dt = timezone.now()
        obj = MagicMock(updated_at=dt, created_at=None)
        sitemap = sm.UserSitemap()
        assert sitemap.lastmod(obj) == dt
        obj = MagicMock(updated_at=None, created_at=dt)
        assert sitemap.lastmod(obj) == dt


class TestCachedSitemapView(unittest.TestCase):
    def test_cached_sitemap_view_returns_view(self):
        sitemaps = {"static": sm.StaticSitemap()}
        view = sm.cached_sitemap_view(sitemaps)
        assert callable(view)
        factory = RequestFactory()
        request = factory.get("/sitemap.xml")
        with patch("apps.sitemaps.sitemaps.sitemap") as mock_sitemap:
            mock_sitemap.return_value = HttpResponse("ok")
            response = view(request)
            assert response.status_code == 200
            assert response.content == b"ok"
            