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

    def changefreq(self, item) -> str:
        """Return the change frequency for a static route item.

        Args:
            item: Dictionary containing static route information.

        Returns:
            str: Change frequency value for the sitemap entry.

        """
        return item["changefreq"]

    def location(self, item) -> str:
        """Return the URL path for a static route item.

        Args:
            item: Dictionary containing static route information.

        Returns:
            str: The URL path for the static route.

        """
        return item["path"]

    def items(self) -> tuple[dict, ...]:
        """Return static routes for sitemap generation.

        Returns:
            tuple: Tuple of dictionaries containing static route configurations.

        """
        return BaseSitemap.STATIC_ROUTES

    def lastmod(self, item: dict) -> datetime:
        """Return the last modification date for a static route item.

        Args:
            item: Dictionary containing static route information.

        Returns:
            datetime: Last modification timestamp based on the most recently updated
                object of the corresponding model, or current time if no model mapping exists.

        """
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
            model.objects.aggregate(latest=Max("updated_at"))["latest"]  #  type: ignore[attr-defined]
            if (model := path_to_model.get(item["path"]))
            else datetime.now(UTC)
        )

    def priority(self, item: dict) -> float:
        """Return the priority score for a static route item.

        Args:
            item: Dictionary containing static route information.

        Returns:
            float: Priority value for the sitemap entry (0.0 to 1.0).

        """
        return item["priority"]
