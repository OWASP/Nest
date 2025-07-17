"""Member sitemap."""

from apps.github.models.user import User
from apps.sitemap.views.base import BaseSitemap


class MemberSitemap(BaseSitemap):
    """Member sitemap."""

    prefix = "/members"

    def items(self):
        """Return list of members for sitemap generation."""
        return [u for u in User.objects.filter(is_bot=False) if u.is_indexable]
