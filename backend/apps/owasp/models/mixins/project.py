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
        """Return the companies for indexing.

        Returns:
            str: A joined string of unique company names from all member organizations.
        """
        return join_values(fields=[o.company for o in self.organizations.all()])

    @property
    def idx_contributors_count(self) -> int:
        """Return the contributors count for indexing.

        Returns:
            int: The total number of contributors to the project.
        """
        return self.contributors_count

    @property
    def idx_custom_tags(self) -> str:
        """Return the custom tags for indexing.

        Returns:
            str: The custom tags associated with the project.
        """
        return self.custom_tags

    @property
    def idx_forks_count(self) -> int:
        """Return the forks count for indexing.

        Returns:
            int: The total number of forks across project repositories.
        """
        return self.forks_count

    @property
    def idx_health_score(self) -> float | None:
        """Return the health score for indexing.

        Returns:
            float | None: The project health score, or a default score if in production.
        """
        # TODO(arkid15r): Enable real health score in production when ready.
        return DEFAULT_HEALTH_SCORE if settings.IS_PRODUCTION_ENVIRONMENT else self.health_score

    @property
    def idx_is_active(self) -> bool:
        """Return the active status for indexing.

        Returns:
            bool: True if the project is active, False otherwise.
        """
        return self.is_active

    @property
    def idx_issues_count(self) -> int:
        """Return the open issues count for indexing.

        Returns:
            int: The total number of open issues in the project.
        """
        return self.open_issues.count()

    @property
    def idx_key(self) -> str:
        """Return the project key for indexing.

        Returns:
            str: The project key without the 'www-project-' prefix.
        """
        return self.key.replace("www-project-", "")

    @property
    def idx_languages(self) -> list[str]:
        """Return the languages for indexing.

        Returns:
            list[str]: A list of languages used in the project's repositories.
        """
        return self.languages

    @property
    def idx_level(self) -> str:
        """Return the level for indexing.

        Returns:
            str: The level of the project.
        """
        return self.level

    @property
    def idx_level_raw(self) -> float | None:
        """Return the raw level for indexing.

        Returns:
            float | None: The raw numeric level of the project.
        """
        return float(self.level_raw) if self.level_raw else None

    @property
    def idx_name(self) -> str:
        """Return the name for indexing.

        Returns:
            str: The project name, or a capitalized version of the key.
        """
        return self.name or " ".join(self.key.replace("www-project-", "").capitalize().split("-"))

    @property
    def idx_organizations(self) -> str:
        """Return the organizations for indexing.

        Returns:
            str: A joined string of organization names associated with the project.
        """
        return join_values(fields=[o.name for o in self.organizations.all()])

    @property
    def idx_repositories(self) -> list[dict]:
        """Return the repositories for indexing.

        Returns:
            list[dict]: A list of dictionaries containing details of project repositories.
        """
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
        """Return the repositories count for indexing.

        Returns:
            int: The total number of repositories in the project.
        """
        return self.repositories.count()

    @property
    def idx_stars_count(self) -> int:
        """Return the stars count for indexing.

        Returns:
            int: The total number of stars received by the project's repositories.
        """
        return self.stars_count

    @property
    def idx_top_contributors(self) -> list:
        """Return the top contributors for indexing.

        Returns:
            list: A list of top contributors in the project.
        """
        return RepositoryContributor.get_top_contributors(project=self.key)

    @property
    def idx_type(self) -> str:
        """Return the project type for indexing.

        Returns:
            str: The type of the project.
        """
        return self.type

    @property
    def idx_updated_at(self) -> str | float:
        """Return the updated at timestamp for indexing.

        Returns:
            str | float: The last update timestamp, or an empty string.
        """
        return self.updated_at.timestamp() if self.updated_at else ""
