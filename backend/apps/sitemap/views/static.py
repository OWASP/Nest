"""Static sitemap."""

from datetime import UTC, datetime

from django.db.models import Max

from apps.github.models.organization import Organization
from apps.github.models.user import User
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.project import Project
from apps.owasp.models.snapshot import Snapshot
from apps.sitemap.views.base import BaseSitemap


class StaticSitemap(BaseSitemap):
    """A sitemap for static routes that includes all other dynamic sitemaps."""

    def changefreq(self, item):
        """Return the change frequency for a static route item."""
        return item["changefreq"]

    def location(self, item):
        """Return the URL path for a static route item."""
        return item["path"]

    def items(self):
        """Return list of static routes for sitemap generation."""
        return BaseSitemap.STATIC_ROUTES

    def lastmod(self, item):
        """Return the last modification date for a static route item."""
        path_to_model = {
            "/chapters": Chapter,
            "/committees": Committee,
            "/contribute": Project,
            "/members": User,
            "/organizations": Organization,
            "/projects": Project,
            "/snapshots": Snapshot,
        }

        return (
            model.objects.aggregate(latest=Max("updated_at"))["latest"]
            if (model := path_to_model.get(item["path"]))
            else datetime.now(UTC)
        )

    def priority(self, item):
        """Return the priority score for a static route item."""
        return item["priority"]
