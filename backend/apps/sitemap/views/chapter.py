"""Chapter sitemap."""

from apps.owasp.models.chapter import Chapter
from apps.sitemap.views.base import BaseSitemap


class ChapterSitemap(BaseSitemap):
    """Chapter sitemap."""

    change_frequency = "weekly"
    prefix = "/chapters"

    def items(self):
        """Return list of chapters for sitemap generation."""
        return [
            c
            for c in Chapter.active_chapters.order_by(
                "-updated_at",
                "-created_at",
            )
            if c.is_indexable
        ]
