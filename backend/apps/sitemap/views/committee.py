"""Committee sitemap."""

from apps.owasp.models.committee import Committee
from apps.sitemap.views.base import BaseSitemap


class CommitteeSitemap(BaseSitemap):
    """Committee sitemap."""

    prefix = "/committees"

    def items(self):
        """Return list of committees for sitemap generation."""
        return [c for c in Committee.objects.filter(is_active=True) if c.is_indexable]
