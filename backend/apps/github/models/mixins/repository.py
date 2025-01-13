"""GitHub repository mixins."""

from apps.github.constants import OWASP_FOUNDATION_LOGIN
from apps.github.models.repository_contributor import (
    TOP_CONTRIBUTORS_LIMIT,
    RepositoryContributor,
)


class RepositoryIndexMixin:
    """Repository index mixin."""

    @property
    def idx_commits_count(self):
        """Return commits count for indexing."""
        return self.commits_count

    @property
    def idx_contributors_count(self):
        """Return contributors count for indexing."""
        return self.contributors_count

    @property
    def idx_created_at(self):
        """Return created at for indexing."""
        return self.created_at.timestamp()

    @property
    def idx_description(self):
        """Return description for indexing."""
        return self.description

    @property
    def idx_forks_count(self):
        """Return forks count for indexing."""
        return self.forks_count

    @property
    def idx_has_funding_yml(self):
        """Return has funding.yml for indexing."""
        return self.has_funding_yml

    @property
    def idx_key(self):
        """Return key for indexing."""
        return self.nest_key

    @property
    def idx_languages(self):
        """Return languages for indexing."""
        return self.languages

    @property
    def idx_license(self):
        """Return license for indexing."""
        return self.license

    @property
    def idx_name(self):
        """Return name for indexing."""
        return self.name

    @property
    def idx_open_issues_count(self):
        """Return open issues count for indexing."""
        return self.open_issues_count

    @property
    def idx_project_key(self):
        """Return project key for indexing."""
        return self.project.nest_key if self.project else ""

    @property
    def idx_pushed_at(self):
        """Return pushed at for indexing."""
        return self.pushed_at.timestamp()

    @property
    def idx_size(self):
        """Return size for indexing."""
        return self.size

    @property
    def idx_stars_count(self):
        """Return stars count for indexing."""
        return self.stars_count

    @property
    def idx_subscribers_count(self):
        """Return subscribers count for indexing."""
        return self.stars_count

    @property
    def idx_top_contributors(self):
        """Return top contributors for indexing."""
        return [
            {
                "avatar_url": tc["user__avatar_url"],
                "contributions_count": tc["contributions_count"],
                "login": tc["user__login"],
                "name": tc["user__name"],
            }
            for tc in RepositoryContributor.objects.filter(repository__in=[self])
            .exclude(user__login__in=[OWASP_FOUNDATION_LOGIN])
            .values(
                "contributions_count",
                "user__avatar_url",
                "user__login",
                "user__name",
            )
            .order_by("-contributions_count")[:TOP_CONTRIBUTORS_LIMIT]
        ]

    @property
    def idx_topics(self):
        """Return topics for indexing."""
        return self.topics

    @property
    def idx_is_archived(self):
        """Return URL for indexing."""
        return self.is_archived
