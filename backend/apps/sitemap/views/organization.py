"""Sitemap views for Organization objects."""

from apps.github.models.organization import Organization
from apps.sitemap.views.base import BaseSitemap


class OrganizationSitemap(BaseSitemap):
    """Sitemap for Organization objects."""

    change_frequency = "monthly"
    prefix = "/organizations"

    def items(self):
        """Return a queryset of indexable Organization objects."""
        return [
            o
            for o in Organization.objects.filter(
                is_owasp_related_organization=True,
            ).order_by(
                "-updated_at",
                "-created_at",
            )
            if o.is_indexable
        ]
