"""Project sitemap."""

from apps.owasp.models.project import Project
from apps.sitemap.views.base import BaseSitemap


class ProjectSitemap(BaseSitemap):
    """Project sitemap."""

    prefix = "/projects"

    def items(self):
        """Return list of projects for sitemap generation."""
        return [p for p in Project.objects.filter(is_active=True) if p.is_indexable]
