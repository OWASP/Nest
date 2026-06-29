"""Member sitemap."""

from apps.github.models.user import User
from apps.sitemap.views.base import BaseSitemap


class MemberSitemap(BaseSitemap):
    """Member sitemap."""

    change_frequency = "daily"
    prefix = "/members"

    def items(self) -> list[User]:
        """Return members for sitemap generation.

        Returns:
            list: List of indexable User objects ordered by update/creation date

        """
        return [
            u
            for u in User.objects.filter(
                is_bot=False,
            ).order_by(
                "-updated_at",
                "-created_at",
            )
            if u.is_indexable
        ]
