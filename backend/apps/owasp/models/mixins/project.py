"""OWASP app project mixins."""

from apps.common.utils import join_values
from apps.owasp.models.mixins.common import GenericEntityMixin

ISSUES_LIMIT = 6
RELEASES_LIMIT = 4
REPOSITORIES_LIMIT = 4


class ProjectIndexMixin(GenericEntityMixin):
    """Project index mixin."""

    @property
    def is_indexable(self):
        """Projects to index."""
        return self.is_active and self.has_active_repositories

    @property
    def idx_companies(self):
        """Return companies for indexing."""
        return join_values(fields=(o.company for o in self.organizations.all()))

    @property
    def idx_contributors_count(self):
        """Return contributors count for indexing."""
        return self.contributors_count

    @property
    def idx_custom_tags(self):
        """Return custom tags for indexing."""
        return self.custom_tags

    @property
    def idx_forks_count(self):
        """Return forks count for indexing."""
        return self.forks_count

    @property
    def idx_is_active(self):
        """Return active status for indexing."""
        return self.is_active

    @property
    def idx_issues_count(self):
        """Return issues count for indexing."""
        return self.open_issues.count()

    @property
    def idx_key(self):
        """Return key for indexing."""
        return self.key.replace("www-project-", "")

    @property
    def idx_languages(self):
        """Return languages for indexing."""
        return self.languages

    @property
    def idx_level(self):
        """Return level text value for indexing."""
        return self.level

    @property
    def idx_level_raw(self):
        """Return level for indexing."""
        return float(self.level_raw) if self.level_raw else None

    @property
    def idx_name(self):
        """Return name for indexing."""
        return self.name or " ".join(self.key.replace("www-project-", "").capitalize().split("-"))

    @property
    def idx_organizations(self):
        """Return organizations for indexing."""
        return join_values(fields=(o.name for o in self.organizations.all()))

    @property
    def idx_repositories(self):
        """Return repositories for indexing."""
        return [
            {
                "contributors_count": r.contributors_count,
                "description": r.description,
                "forks_count": r.forks_count,
                "key": r.key.lower(),
                "latest_release": str(r.latest_release.summary) if r.latest_release else "",
                "license": r.license,
                "name": r.name,
                "owner_key": r.owner.login.lower(),
                "stars_count": r.stars_count,
            }
            for r in self.repositories.order_by("-stars_count")[:REPOSITORIES_LIMIT]
        ]

    @property
    def idx_repositories_count(self):
        """Return repositories count for indexing."""
        return self.repositories.count()

    @property
    def idx_stars_count(self):
        """Return stars count for indexing."""
        return self.stars_count

    @property
    def idx_top_contributors(self):
        """Return top contributors for indexing."""
        return super().get_top_contributors(repositories=self.repositories.all())

    @property
    def idx_type(self):
        """Return type for indexing."""
        return self.type

    @property
    def idx_updated_at(self):
        """Return updated at for indexing."""
        return self.updated_at.timestamp() if self.updated_at else ""
