"""Snapshot sitemap."""

from apps.owasp.models.snapshot import Snapshot
from apps.sitemap.views.base import BaseSitemap


class SnapshotSitemap(BaseSitemap):
    """Sitemap for Snapshot  objects."""

    change_frequency = "monthly"
    prefix = "/snapshots"

    def items(self):
        """Return queryset of snapshots for sitemap generation."""
        return Snapshot.objects.filter(
            status=Snapshot.Status.COMPLETED,
        ).order_by(
            "-updated_at",
            "-created_at",
        )

    def location(self, obj):
        """Return the URL path for an object."""
        return f"{self.prefix}/{obj.key}"
