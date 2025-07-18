import math
from unittest.mock import MagicMock

import pytest
from django.utils import timezone

from apps.sitemap.views.base import BaseSitemap


@pytest.fixture
def sitemap():
    return BaseSitemap()


class TestBaseSitemap:
    def test_changefreq(self, sitemap):
        obj = MagicMock()

        assert sitemap.changefreq(obj) == "weekly"

    def test_get_protocol(self, sitemap):
        assert sitemap.get_protocol() == "https"

    def test_get_static_priority_for_known_path(self, sitemap):
        assert math.isclose(sitemap.get_static_priority("/projects"), 0.9)
        assert math.isclose(sitemap.get_static_priority("/chapters"), 0.8)

    def test_get_static_priority_for_unknown_path(self, sitemap):
        assert math.isclose(sitemap.get_static_priority("/unknown"), 0.7)

    def test_lastmod_with_created_at(self, sitemap):
        dt = timezone.now()
        obj = MagicMock(updated_at=None, created_at=dt)

        assert sitemap.lastmod(obj) == dt

    def test_lastmod_with_updated_at(self, sitemap):
        dt = timezone.now()
        obj = MagicMock(updated_at=dt, created_at=None)

        assert sitemap.lastmod(obj) == dt

    def test_limit(self, sitemap):
        assert sitemap.limit == 50000

    def test_location(self, sitemap):
        obj = MagicMock(nest_key="test")

        assert sitemap.location(obj) == "/test"

    def test_priority(self, sitemap):
        obj = MagicMock()

        assert math.isclose(sitemap.priority(obj), 0.7)
