"""Snapshot sitemap."""

from apps.owasp.models.snapshot import Snapshot
from apps.sitemap.views.base import BaseSitemap


class SnapshotSitemap(BaseSitemap):
    """Sitemap for Snapshot  objects."""

    change_frequency = "weekly"
    prefix = "/snapshots"

    def items(self):
        """Return a queryset of indexable Snapshot objects."""
        return [
            s
            for s in Snapshot.objects.filter(
                status=Snapshot.Status.COMPLETED
            ).order_by(
                "-updated_at", 
                "-created_at"
            )
            if s.is_indexable
        ]
