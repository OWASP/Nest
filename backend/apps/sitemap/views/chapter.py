"""Chapter sitemap."""

from apps.owasp.models.chapter import Chapter
from apps.sitemap.views.base import BaseSitemap


class ChapterSitemap(BaseSitemap):
    """Chapter sitemap."""

    prefix = "/chapters"

    def items(self):
        """Return list of chapters for sitemap generation."""
        return [c for c in Chapter.objects.filter(is_active=True) if c.is_indexable]
