"""Snapshot sitemap."""

from django.db.models import QuerySet

from apps.owasp.models.snapshot import Snapshot
from apps.sitemap.views.base import BaseSitemap


class SnapshotSitemap(BaseSitemap):
    """Sitemap for Snapshot  objects."""

    change_frequency = "monthly"
    prefix = "/snapshots"

    def items(self) -> QuerySet[Snapshot]:
        """Return snapshots for sitemap generation.

        Returns:
            QuerySet: Queryset of completed Snapshot objects ordered by update/creation date.

        """
        return Snapshot.objects.filter(
            status=Snapshot.Status.COMPLETED,
        ).order_by(
            "-updated_at",
            "-created_at",
        )

    def location(self, obj):
        """Return the URL path for a snapshot.

        Args:
            obj: Snapshot instance to generate URL for.

        Returns:
            str: The URL path for the snapshot.

        """
        return f"{self.prefix}/{obj.key}"
