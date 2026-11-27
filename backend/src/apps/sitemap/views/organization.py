"""Sitemap views for Organization objects."""

from apps.github.models.organization import Organization
from apps.sitemap.views.base import BaseSitemap


class OrganizationSitemap(BaseSitemap):
    """Sitemap for Organization objects."""

    change_frequency = "monthly"
    prefix = "/organizations"

    def items(self) -> list[Organization]:
        """Return organizations for sitemap generation.

        Returns:
            list: List of indexable OWASP-related Organization objects
                ordered by update/creation date.

        """
        return [
            o
            for o in Organization.related_organizations.order_by(
                "-updated_at",
                "-created_at",
            )
            if o.is_indexable
        ]
