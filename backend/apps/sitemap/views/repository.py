"""Repository sitemap."""

from apps.github.models.repository import Repository
from apps.sitemap.views.base import BaseSitemap


class RepositorySitemap(BaseSitemap):
    """Repository sitemap."""

    change_frequency = "weekly"
    prefix = "/repositories"

    def items(self) -> list[Repository]:
        """Return repositories for sitemap generation.

        Returns:
            list[Repository]: List of indexable Repository objects ordered by
                update/creation date.

        """
        return [
            r
            for r in Repository.objects.order_by(
                "-updated_at",
                "-created_at",
            )
            if r.organization and r.is_indexable
        ]

    def location(self, obj: Repository) -> str:
        """Return the URL path for a repository.

        Args:
            obj: Repository instance to generate URL for.

        Returns:
            str: The URL path for the repository.

        """
        return f"/organizations/{obj.organization.nest_key}{self.prefix}/{obj.key}"
