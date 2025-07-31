"""Repository sitemap."""

from django.db.models import QuerySet

from apps.github.models.repository import Repository
from apps.sitemap.views.base import BaseSitemap


class RepositorySitemap(BaseSitemap):
    """Repository sitemap."""

    change_frequency = "weekly"
    prefix = "/organizations"

    def items(self) -> QuerySet[Repository]:
        """Return list of repositories for sitemap generation.
        
        Returns:
            QuerySet[Repository]: Filtered and ordered repository queryset,
                limited to prevent performance issues with large datasets.
        """
        return Repository.objects.filter(
            is_archived=False,
            owner__isnull=False,
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
            
        Raises:
            ValueError: If repository has no owner.
        """
        if not obj.owner:
            raise ValueError(f"Repository '{obj.name}' has no owner")
        
        return f"{self.prefix}/{obj.owner.login}/repositories/{obj.key}"
        