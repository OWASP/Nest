from http import HTTPStatus
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory

from apps.sitemap.views import StaticSitemap, cached_sitemap_view


class TestCachedSitemapView:
    def test_cached_sitemap_view_returns_view(self):
        sitemaps = {"static": StaticSitemap()}
        view = cached_sitemap_view(sitemaps)

        assert callable(view)

        factory = RequestFactory()
        request = factory.get("/sitemap.xml")
        with patch("apps.sitemap.views.sitemap") as mock_sitemap:
            mock_sitemap.return_value = HttpResponse("ok")
            response = view(request)

        assert response.status_code == HTTPStatus.OK
        assert response.content == b"ok"
