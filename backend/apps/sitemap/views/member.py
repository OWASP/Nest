"""Member sitemap."""

from django.contrib.sitemaps import Sitemap

from apps.github.models.user import User


class MemberSitemap(Sitemap):
    """Member sitemap."""

    prefix = "/members"

    def items(self):
        """Return list of members for sitemap generation."""
        return [u for u in User.objects.filter(is_bot=False) if u.is_indexable]
