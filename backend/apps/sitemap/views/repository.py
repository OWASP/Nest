"""Repository sitemap."""

from django.db.models import QuerySet

from apps.github.models.repository import Repository
from apps.sitemap.views.base import BaseSitemap


class RepositorySitemap(BaseSitemap):
    """Repository sitemap."""

    change_frequency = "weekly"
    prefix = "/repositories"

    def items(self) -> QuerySet[Repository]:
        """Return list of repositories for sitemap generation.

        Returns:
            QuerySet[Repository]: Queryset of non-archived, non-empty, non-template repositories
                with organizations, ordered by update/creation date.

        """
        return Repository.objects.filter(
            is_archived=False,
            is_empty=False,
            is_template=False,
            organization__isnull=False,
        ).order_by(
            "-updated_at",
            "-created_at",
        )

    def location(self, obj: Repository) -> str:
        """Return the URL path for a repository.

        Args:
            obj: Repository instance to generate URL for.

        Returns:
            str: The URL path for the repository.

        """
        return f"/organizations/{obj.organization.nest_key}{self.prefix}/{obj.key}"
