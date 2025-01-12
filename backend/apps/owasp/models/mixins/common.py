"""OWASP app common models."""

from django.db.models import Sum

from apps.github.constants import OWASP_FOUNDATION_LOGIN
from apps.github.models.repository_contributor import (
    TOP_CONTRIBUTORS_LIMIT,
    RepositoryContributor,
)


class GenericEntityMixin:
    """OWASP Entity mixin."""

    def get_top_contributors(self, repositories=()):
        """Get top contributors."""
        return [
            {
                "avatar_url": tc["user__avatar_url"],
                "contributions_count": tc["total_contributions"],
                "login": tc["user__login"],
                "name": tc["user__name"],
            }
            for tc in RepositoryContributor.objects.filter(repository__in=repositories)
            .exclude(user__login__in=[OWASP_FOUNDATION_LOGIN])
            .values(
                "user__avatar_url",
                "user__login",
                "user__name",
            )
            .annotate(total_contributions=Sum("contributions_count"))
            .order_by("-total_contributions")[:TOP_CONTRIBUTORS_LIMIT]
        ]

    @property
    def idx_description(self):
        """Return description for indexing."""
        return self.description

    @property
    def idx_leaders(self):
        """Return leaders for indexing."""
        return [leader for leader in self.leaders_raw if not leader.startswith("@")]

    @property
    def idx_name(self):
        """Return name for indexing."""
        return self.name

    @property
    def idx_summary(self):
        """Return summary for indexing."""
        return self.summary

    @property
    def idx_tags(self):
        """Return tags for indexing."""
        return self.tags

    @property
    def idx_topics(self):
        """Return topics for indexing."""
        return self.topics

    @property
    def idx_url(self):
        """Return URL for indexing."""
        return self.owasp_url

    @property
    def is_indexable(self):
        """Entities to index."""
        return self.is_active and self.has_active_repositories

    @property
    def github_url(self):
        """Get GitHub URL."""
        return f"https://github.com/owasp/{self.key}"

    @property
    def owasp_url(self):
        """Get OWASP URL."""
        return f"https://owasp.org/{self.key}"