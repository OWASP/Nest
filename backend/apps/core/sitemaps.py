from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.http import HttpRequest
from apps.owasp.models.project import Project
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.github.models.user import User
from django.db.models import Max
from datetime import datetime, UTC

# Static routes 
STATIC_ROUTES = [
    {"path": "/chapters", "changefreq": "weekly", "priority": 0.8},
    {"path": "/committees", "changefreq": "monthly", "priority": 0.8},
    {"path": "/projects", "changefreq": "weekly", "priority": 0.9},
    {"path": "/contribute", "changefreq": "daily", "priority": 0.6},
    {"path": "/members", "changefreq": "daily", "priority": 0.7},
]

class StaticSitemap(Sitemap):
    '''A sitemap for static routes that includes all other dynamic sitemaps.'''
    def items(self):
        return STATIC_ROUTES

    def location(self, item):
        return item["path"]

    def changefreq(self, item):
        return item["changefreq"]

    def priority(self, item):
        return item["priority"]

    def lastmod(self, item):
        if item["path"] in ["/projects", "/contribute"]:
            lastmod = Project.objects.aggregate(latest=Max("created_at"))['latest']
        elif item["path"] == "/chapters":
            lastmod = Chapter.objects.aggregate(latest=Max("created_at"))['latest']
        elif item["path"] == "/committees":
            lastmod = Committee.objects.aggregate(latest=Max("created_at"))['latest']
        elif item["path"] == "/members":
            lastmod = User.objects.aggregate(latest=Max("created_at"))['latest']
        else:
            lastmod = None
        return lastmod or datetime.now(UTC)

def get_static_priority(path):
    '''Get the priority for a static route based on its path.'''
    for route in STATIC_ROUTES:
        if route["path"] == path:
            return route["priority"]
    return 0.7  # fallback priority

class ProjectSitemap(Sitemap):
    '''Sitemap for projects.'''
    def items(self):
        return [p for p in Project.objects.all() if getattr(p, 'is_indexable', True)]

    def location(self, obj):
        return f"/projects/{obj.nest_key}"

    def changefreq(self, obj):
        return "weekly"

    def priority(self, obj):
        return get_static_priority("/projects")

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at

class ChapterSitemap(Sitemap):
    '''Sitemap for chapters.'''
    def items(self):
        return [c for c in Chapter.objects.filter(is_active=True) if getattr(c, 'is_indexable', True)]

    def location(self, obj):
        return f"/chapters/{obj.nest_key}"

    def changefreq(self, obj):
        return "weekly"

    def priority(self, obj):
        return get_static_priority("/chapters")

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at

class CommitteeSitemap(Sitemap):
    '''Sitemap for committees.'''
    def items(self):
        return [c for c in Committee.objects.filter(is_active=True) if getattr(c, 'is_indexable', True)]

    def location(self, obj):
        return f"/committees/{obj.nest_key}"

    def changefreq(self, obj):
        return "weekly"

    def priority(self, obj):
        return get_static_priority("/committees")

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at

class UserSitemap(Sitemap):
    '''Sitemap for users.'''
    def items(self):
        return [u for u in User.objects.all() if getattr(u, 'is_indexable', True)]

    def location(self, obj):
        return f"/members/{obj.login}"

    def changefreq(self, obj):
        return "weekly"

    def priority(self, obj):
        return get_static_priority("/members")

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at

# Cached sitemap views
def cached_sitemap_view(sitemaps, **kwargs):
    '''Caching site map view for performance.'''
    @cache_page(settings.SITEMAP_CACHE_TIMEOUT)
    def _view(request: HttpRequest):
        return sitemap(request, sitemaps=sitemaps, **kwargs)
    return _view