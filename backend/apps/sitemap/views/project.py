"""Project sitemap."""

from django.contrib.sitemaps import Sitemap

from apps.owasp.models.project import Project


class ProjectSitemap(Sitemap):
    """Project sitemap."""

    prefix = "/projects"

    def items(self):
        """Return list of projects for sitemap generation."""
        return [p for p in Project.objects.filter(is_active=True) if p.is_indexable]
