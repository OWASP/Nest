"""Django sitemap configuration with static and dynamic routes."""

from datetime import UTC, datetime

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.db.models import Max
from django.http import HttpRequest
from django.views.decorators.cache import cache_page

from apps.github.models.user import User
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.project import Project

# Static routes
STATIC_ROUTES = [
    {"path": "/chapters", "changefreq": "weekly", "priority": 0.8},
    {"path": "/committees", "changefreq": "monthly", "priority": 0.8},
    {"path": "/projects", "changefreq": "weekly", "priority": 0.9},
    {"path": "/contribute", "changefreq": "daily", "priority": 0.6},
    {"path": "/members", "changefreq": "daily", "priority": 0.7},
]


class StaticSitemap(Sitemap):
    """A sitemap for static routes that includes all other dynamic sitemaps."""

    def items(self):
        """Return list of static routes for sitemap generation."""
        return STATIC_ROUTES

    def location(self, item):
        """Return the URL path for a static route item."""
        return item["path"]

    def changefreq(self, item):
        """Return the change frequency for a static route item."""
        return item["changefreq"]

    def priority(self, item):
        """Return the priority score for a static route item."""
        return item["priority"]

    def lastmod(self, item):
        """Return the last modification date for a static route item."""
        path_to_model = {
            "/projects": Project,
            "/contribute": Project,
            "/chapters": Chapter,
            "/committees": Committee,
            "/members": User,
        }
        model = path_to_model.get(item["path"])
        if model:
            lastmod = model.objects.aggregate(latest=Max("updated_at"))["latest"]
        else:
            lastmod = None
        return lastmod or datetime.now(UTC)


def get_static_priority(path):
    """Get the priority for a static route based on its path."""
    for route in STATIC_ROUTES:
        if route["path"] == path:
            return route["priority"]
    return 0.7  # fallback priority


class ProjectSitemap(Sitemap):
    """Sitemap for projects."""

    def items(self):
        """Return list of indexable projects for sitemap generation."""
        return [p for p in Project.objects.all() if getattr(p, "is_indexable", True)]

    def location(self, obj):
        """Return the URL path for a project object."""
        return f"/projects/{obj.nest_key}"

    def changefreq(self, obj):
        """Return the change frequency for a project object."""
        return "weekly"

    def priority(self, obj):
        """Return the priority score for a project object."""
        return get_static_priority("/projects")

    def lastmod(self, obj):
        """Return the last modification date for a project object."""
        return obj.updated_at or obj.created_at


class ChapterSitemap(Sitemap):
    """Sitemap for chapters."""

    def items(self):
        """Return list of active and indexable chapters for sitemap generation."""
        return [
            c for c in Chapter.objects.filter(is_active=True) if getattr(c, "is_indexable", True)
        ]

    def location(self, obj):
        """Return the URL path for a chapter object."""
        return f"/chapters/{obj.nest_key}"

    def changefreq(self, obj):
        """Return the change frequency for a chapter object."""
        return "weekly"

    def priority(self, obj):
        """Return the priority score for a chapter object."""
        return get_static_priority("/chapters")

    def lastmod(self, obj):
        """Return the last modification date for a chapter object."""
        return obj.updated_at or obj.created_at


class CommitteeSitemap(Sitemap):
    """Sitemap for committees."""

    def items(self):
        """Return list of active and indexable committees for sitemap generation."""
        return [
            c for c in Committee.objects.filter(is_active=True) if getattr(c, "is_indexable", True)
        ]

    def location(self, obj):
        """Return the URL path for a committee object."""
        return f"/committees/{obj.nest_key}"

    def changefreq(self, obj):
        """Return the change frequency for a committee object."""
        return "weekly"

    def priority(self, obj):
        """Return the priority score for a committee object."""
        return get_static_priority("/committees")

    def lastmod(self, obj):
        """Return the last modification date for a committee object."""
        return obj.updated_at or obj.created_at


class UserSitemap(Sitemap):
    """Sitemap for users."""

    def items(self):
        """Return list of indexable users for sitemap generation."""
        return [u for u in User.objects.all() if getattr(u, "is_indexable", True)]

    def location(self, obj):
        """Return the URL path for a user object."""
        return f"/members/{obj.login}"

    def changefreq(self, obj):
        """Return the change frequency for a user object."""
        return "weekly"

    def priority(self, obj):
        """Return the priority score for a user object."""
        return get_static_priority("/members")

    def lastmod(self, obj):
        """Return the last modification date for a user object."""
        return obj.updated_at or obj.created_at


# Cached sitemap views
def cached_sitemap_view(sitemaps, **kwargs):
    """Cache sitemap view for performance optimization."""

    @cache_page(settings.SITEMAP_CACHE_TIMEOUT)
    def _view(request: HttpRequest):
        return sitemap(request, sitemaps=sitemaps, **kwargs)

    return _view
