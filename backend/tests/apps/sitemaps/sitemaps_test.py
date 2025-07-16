import unittest
from unittest.mock import patch, MagicMock
from django.test import RequestFactory
from django.utils import timezone
from django.http import HttpResponse

from apps.sitemaps import sitemaps as sm

class TestStaticSitemap(unittest.TestCase):
    def setUp(self):
        self.sitemap = sm.StaticSitemap()

    @patch("apps.sitemaps.sitemaps.Chapter.objects.aggregate")
    @patch("apps.sitemaps.sitemaps.Committee.objects.aggregate")
    @patch("apps.sitemaps.sitemaps.Project.objects.aggregate")
    @patch("apps.sitemaps.sitemaps.User.objects.aggregate")
    def test_lastmod(self, user_agg, project_agg, committee_agg, chapter_agg):
        dt = timezone.now()
        chapter_agg.return_value = {"latest": dt}
        committee_agg.return_value = {"latest": dt}
        project_agg.return_value = {"latest": dt}
        user_agg.return_value = {"latest": dt}
        for item in sm.STATIC_ROUTES:
            result = self.sitemap.lastmod(item)
            self.assertIsNotNone(result)

    def test_items(self):
        self.assertEqual(self.sitemap.items(), sm.STATIC_ROUTES)

    def test_location(self):
        for item in sm.STATIC_ROUTES:
            self.assertEqual(self.sitemap.location(item), item["path"])

    def test_changefreq(self):
        for item in sm.STATIC_ROUTES:
            self.assertEqual(self.sitemap.changefreq(item), item["changefreq"])

    def test_priority(self):
        for item in sm.STATIC_ROUTES:
            self.assertEqual(self.sitemap.priority(item), item["priority"])

class TestGetStaticPriority(unittest.TestCase):
    def test_priority_for_known_path(self):
        self.assertEqual(sm.get_static_priority("/projects"), 0.9)
        self.assertEqual(sm.get_static_priority("/chapters"), 0.8)
    def test_priority_for_unknown_path(self):
        self.assertEqual(sm.get_static_priority("/unknown"), 0.7)

class TestProjectSitemap(unittest.TestCase):
    @patch("apps.sitemaps.sitemaps.Project")
    def test_items(self, Project):
        mock_obj = MagicMock(is_indexable=True)
        Project.objects.filter.return_value = [mock_obj]
        sitemap = sm.ProjectSitemap()
        self.assertEqual(list(sitemap.items()), [mock_obj])

    def test_location(self):
        obj = MagicMock(nest_key="foo")
        sitemap = sm.ProjectSitemap()
        self.assertEqual(sitemap.location(obj), "/projects/foo")

    def test_changefreq(self):
        obj = MagicMock()
        sitemap = sm.ProjectSitemap()
        self.assertEqual(sitemap.changefreq(obj), "weekly")

    def test_priority(self):
        obj = MagicMock()
        sitemap = sm.ProjectSitemap()
        self.assertEqual(sitemap.priority(obj), sm.get_static_priority("/projects"))

    def test_lastmod(self):
        dt = timezone.now()
        obj = MagicMock(updated_at=dt, created_at=None)
        sitemap = sm.ProjectSitemap()
        self.assertEqual(sitemap.lastmod(obj), dt)
        obj = MagicMock(updated_at=None, created_at=dt)
        self.assertEqual(sitemap.lastmod(obj), dt)

class TestChapterSitemap(unittest.TestCase):
    @patch("apps.sitemaps.sitemaps.Chapter")
    def test_items(self, Chapter):
        mock_obj = MagicMock(is_indexable=True)
        Chapter.objects.filter.return_value = [mock_obj]
        sitemap = sm.ChapterSitemap()
        self.assertEqual(list(sitemap.items()), [mock_obj])

    def test_location(self):
        obj = MagicMock(nest_key="bar")
        sitemap = sm.ChapterSitemap()
        self.assertEqual(sitemap.location(obj), "/chapters/bar")

    def test_changefreq(self):
        obj = MagicMock()
        sitemap = sm.ChapterSitemap()
        self.assertEqual(sitemap.changefreq(obj), "weekly")

    def test_priority(self):
        obj = MagicMock()
        sitemap = sm.ChapterSitemap()
        self.assertEqual(sitemap.priority(obj), sm.get_static_priority("/chapters"))

    def test_lastmod(self):
        dt = timezone.now()
        obj = MagicMock(updated_at=dt, created_at=None)
        sitemap = sm.ChapterSitemap()
        self.assertEqual(sitemap.lastmod(obj), dt)
        obj = MagicMock(updated_at=None, created_at=dt)
        self.assertEqual(sitemap.lastmod(obj), dt)

class TestCommitteeSitemap(unittest.TestCase):
    @patch("apps.sitemaps.sitemaps.Committee")
    def test_items(self, Committee):
        mock_obj = MagicMock(is_indexable=True)
        Committee.objects.filter.return_value = [mock_obj]
        sitemap = sm.CommitteeSitemap()
        self.assertEqual(list(sitemap.items()), [mock_obj])

    def test_location(self):
        obj = MagicMock(nest_key="baz")
        sitemap = sm.CommitteeSitemap()
        self.assertEqual(sitemap.location(obj), "/committees/baz")

    def test_changefreq(self):
        obj = MagicMock()
        sitemap = sm.CommitteeSitemap()
        self.assertEqual(sitemap.changefreq(obj), "weekly")

    def test_priority(self):
        obj = MagicMock()
        sitemap = sm.CommitteeSitemap()
        self.assertEqual(sitemap.priority(obj), sm.get_static_priority("/committees"))

    def test_lastmod(self):
        dt = timezone.now()
        obj = MagicMock(updated_at=dt, created_at=None)
        sitemap = sm.CommitteeSitemap()
        self.assertEqual(sitemap.lastmod(obj), dt)
        obj = MagicMock(updated_at=None, created_at=dt)
        self.assertEqual(sitemap.lastmod(obj), dt)

class TestUserSitemap(unittest.TestCase):
    @patch("apps.sitemaps.sitemaps.User")
    def test_items(self, User):
        mock_obj = MagicMock(is_indexable=True)
        User.objects.filter.return_value = [mock_obj]
        sitemap = sm.UserSitemap()
        self.assertEqual(list(sitemap.items()), [mock_obj])

    def test_location(self):
        obj = MagicMock(login="qux")
        sitemap = sm.UserSitemap()
        self.assertEqual(sitemap.location(obj), "/members/qux")

    def test_changefreq(self):
        obj = MagicMock()
        sitemap = sm.UserSitemap()
        self.assertEqual(sitemap.changefreq(obj), "weekly")

    def test_priority(self):
        obj = MagicMock()
        sitemap = sm.UserSitemap()
        self.assertEqual(sitemap.priority(obj), sm.get_static_priority("/members"))

    def test_lastmod(self):
        dt = timezone.now()
        obj = MagicMock(updated_at=dt, created_at=None)
        sitemap = sm.UserSitemap()
        self.assertEqual(sitemap.lastmod(obj), dt)
        obj = MagicMock(updated_at=None, created_at=dt)
        self.assertEqual(sitemap.lastmod(obj), dt)

class TestCachedSitemapView(unittest.TestCase):
    def test_cached_sitemap_view_returns_view(self):
        sitemaps = {"static": sm.StaticSitemap()}
        view = sm.cached_sitemap_view(sitemaps)
        self.assertTrue(callable(view))
        factory = RequestFactory()
        request = factory.get("/sitemap.xml")
        with patch("apps.sitemaps.sitemaps.sitemap") as mock_sitemap:
            mock_sitemap.return_value = HttpResponse("ok")
            response = view(request)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"ok") 