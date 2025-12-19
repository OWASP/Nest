"""OWASP app project mixins."""

from __future__ import annotations

from django.conf import settings

from apps.common.utils import join_values
from apps.github.models.repository_contributor import RepositoryContributor
from apps.owasp.models.mixins.common import RepositoryBasedEntityModelMixin

DEFAULT_HEALTH_SCORE = 100
ISSUES_LIMIT = 6
RELEASES_LIMIT = 4
REPOSITORIES_LIMIT = 4


class ProjectIndexMixin(RepositoryBasedEntityModelMixin):
    """Project index mixin."""

    @property
    def idx_companies(self) -> str:
        """Return companies for indexing."""
        return join_values(fields=[o.company for o in self.organizations.all()])

    @property
    def idx_contributors_count(self) -> int:
        """Return contributors count for indexing."""
        return self.contributors_count

    @property
    def idx_custom_tags(self) -> str:
        """Return custom tags for indexing."""
        return self.custom_tags

    @property
    def idx_forks_count(self) -> int:
        """Return forks count for indexing."""
        return self.forks_count

    @property
    def idx_health_score(self) -> float | None:
        """Return health score for indexing."""
        # TODO(arkid15r): Enable real health score in production when ready.
        return DEFAULT_HEALTH_SCORE if settings.IS_PRODUCTION_ENVIRONMENT else self.health_score

    @property
    def idx_is_active(self) -> bool:
        """Return active status for indexing."""
        return self.is_active

    @property
    def idx_issues_count(self) -> int:
        """Return issues count for indexing."""
        return self.open_issues.count()

    @property
    def idx_key(self) -> str:
        """Return key for indexing."""
        return self.key.replace("www-project-", "")

    @property
    def idx_languages(self) -> list[str]:
        """Return languages for indexing."""
        return self.languages

    @property
    def idx_level(self) -> str:
        """Return level text value for indexing."""
        return self.level

    @property
    def idx_level_raw(self) -> float | None:
        """Return level for indexing."""
        return float(self.level_raw) if self.level_raw else None

    @property
    def idx_name(self) -> str:
        """Return name for indexing."""
        return self.name or " ".join(self.key.replace("www-project-", "").capitalize().split("-"))

    @property
    def idx_organizations(self) -> str:
        """Return organizations for indexing."""
        return join_values(fields=[o.name for o in self.organizations.all()])

    @property
    def idx_repositories(self) -> list[dict]:
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
    def idx_repositories_count(self) -> int:
        """Return repositories count for indexing."""
        return self.repositories.count()

    @property
    def idx_stars_count(self) -> int:
        """Return stars count for indexing."""
        return self.stars_count

    @property
    def idx_top_contributors(self) -> list:
        """Return top contributors for indexing."""
        return RepositoryContributor.get_top_contributors(project=self.key)

    @property
    def idx_type(self) -> str:
        """Return type for indexing."""
        return self.type

    @property
    def idx_updated_at(self) -> str | float:
        """Return updated at for indexing."""
        return self.updated_at.timestamp() if self.updated_at else ""

    @property
    def idx_related_urls(self) -> list:
        """Return related URLs for indexing."""
        return self.related_urls
