"""Organization sitemap."""

from apps.github.models.organization import Organization
from apps.sitemap.views.base import BaseSitemap


class OrganizationSitemap(BaseSitemap):
    """Organization sitemap."""

    change_frequency = "weekly"
    prefix = "/organizations"

    def items(self):
        return Organization.objects.filter(is_indexable=True).order_by(
            "-updated_at", "-created_at"
        )
