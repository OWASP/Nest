"""Sitemap views for Organization objects."""

from apps.github.models.organization import Organization
from apps.sitemap.views.base import BaseSitemap


class OrganizationSitemap(BaseSitemap):
    """Sitemap for Organization objects."""

    change_frequency = "monthly"
    prefix = "/organizations"

    def items(self):
        """Return a list of indexable Organization objects for sitemap generation.

        Returns:
            list: List of indexable OWASP-related Organization objects
                ordered by update/creation date.

        """
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
