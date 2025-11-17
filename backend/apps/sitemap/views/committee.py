"""Committee sitemap."""

from apps.owasp.models.committee import Committee
from apps.sitemap.views.base import BaseSitemap


class CommitteeSitemap(BaseSitemap):
    """Committee sitemap."""

    change_frequency = "monthly"
    prefix = "/committees"

    def items(self):
        """Return list of committees for sitemap generation.

        Returns:
            list: List of indexable Committee objects ordered by update/creation date.

        """
        return [
            c
            for c in Committee.active_committees.order_by(
                "-updated_at",
                "-created_at",
            )
            if c.is_indexable
        ]
