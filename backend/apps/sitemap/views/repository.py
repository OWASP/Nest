"""Repository sitemap."""

from apps.github.models.repository import Repository
from apps.sitemap.views.base import BaseSitemap

class RepositorySitemap(BaseSitemap):
  """Repository sitemap."""

  change_frequency = "weekly"
  prefix = "/repositories"

  def items(self):
    """Return list of repositories for sitemap generation."""
    return Repository.objects.filter(
      is_archived=False,
      is_empty=False,
      is_fork=False,
      is_owasp_repository=True,
    ).order_by("-updated_at","-created_at")
  
  def lastmod(self, obj):
        """Return the last modification date."""
        return obj.updated_at

  def location(self, obj):
        """Return the absolute (GitHub) URL."""
        return obj.url