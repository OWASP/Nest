"""Chapter sitemap."""

from apps.owasp.models.chapter import Chapter
from apps.sitemap.views.base import BaseSitemap


class ChapterSitemap(BaseSitemap):
    """Chapter sitemap."""

    change_frequency = "weekly"
    prefix = "/chapters"

    def items(self) -> list[Chapter]:
        """Return chapters for sitemap generation.

        Returns:
            list: List of indexable Chapter objects ordered by update/creation date.

        """
        return [
            c
            for c in Chapter.active_chapters.order_by(
                "-updated_at",
                "-created_at",
            )
            if c.is_indexable
        ]
