"""Project sitemap."""

from apps.owasp.models.project import Project
from apps.sitemap.views.base import BaseSitemap


class ProjectSitemap(BaseSitemap):
    """Project sitemap."""

    change_frequency = "weekly"
    prefix = "/projects"

    def items(self):
        """Return list of projects for sitemap generation."""
        return [
            p
            for p in Project.active_projects.order_by(
                "-updated_at",
                "-created_at",
            )
            if p.is_indexable
        ]
