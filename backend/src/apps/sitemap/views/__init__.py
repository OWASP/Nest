"""Sitemap views."""

from django.contrib.sitemaps.views import sitemap
from django.http import HttpRequest
from django.views.decorators.cache import cache_page

from .chapter import ChapterSitemap
from .committee import CommitteeSitemap
from .member import MemberSitemap
from .organization import OrganizationSitemap
from .project import ProjectSitemap
from .repository import RepositorySitemap
from .snapshot import SnapshotSitemap
from .static import StaticSitemap


def cached_sitemap_view(sitemaps, **kwargs):
    """Cache sitemap view for performance optimization."""

    @cache_page(86400)  # Cache for 24 hours.
    def _view(request: HttpRequest):
        return sitemap(request, sitemaps=sitemaps, **kwargs)

    return _view
