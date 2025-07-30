"""Sitemap views for Organization objects."""

from apps.organization.models.organization import Organization
from apps.sitemap.views.base import BaseSitemap


class OrganizationSitemap(BaseSitemap):
    """Sitemap for Organization objects."""

    change_frequency = "monthly"
    prefix = "/organizations"

    def items(self):
        """Return a queryset of indexable Organization objects.

        Ordered by updated_at (descending) and created_at (descending).
        """
        return Organization.objects.filter(is_indexable=True).order_by(
            "-updated_at", "-created_at"
        )
