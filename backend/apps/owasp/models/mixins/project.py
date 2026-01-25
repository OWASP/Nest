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
        """Return associated company names for indexing.

        This aggregates the company names of all organizations
        linked to the project and formats them for search indexing.

        Returns:
            str: A concatenated string of company names.
        """
        return join_values(fields=[o.company for o in self.organizations.all()])

    @property
    def idx_contributors_count(self) -> int:
        """Return the number of contributors for indexing.

        This represents how many contributors are associated
        with the project.

        Returns:
            int: The total contributor count.
        """
        return self.contributors_count

    @property
    def idx_custom_tags(self) -> str:
        """Return custom tags for indexing.

        These tags are used to improve search and filtering
        of OWASP projects.

        Returns:
            str: The custom tags associated with the project.
        """
        return self.custom_tags

    @property
    def idx_forks_count(self) -> int:
        """Return the total fork count for indexing.

        This represents how many times project repositories
        have been forked.

        Returns:
            int: The fork count.
        """
        return self.forks_count

    @property
    def idx_health_score(self) -> float | None:
        """Return the project health score for indexing.

        In production environments, a default health score
        is returned until the real scoring system is enabled.
        In non-production environments, the stored health
        score is used.

        Returns:
            float | None: The project health score.
        """
        return DEFAULT_HEALTH_SCORE if settings.IS_PRODUCTION_ENVIRONMENT else self.health_score

    @property
    def idx_is_active(self) -> bool:
        """Return whether the project is active for indexing.

        This indicates if the project is currently active
        and should be shown in search results.

        Returns:
            bool: True if the project is active, False otherwise.
        """
        return self.is_active

    @property
    def idx_issues_count(self) -> int:
        """Return the number of open issues for indexing.

        This value represents how many issues are currently
        open across the project.

        Returns:
            int: The open issue count.
        """
        return self.open_issues.count()

    @property
    def idx_key(self) -> str:
        """Return the project key for indexing.

        The key is normalized by removing the standard
        'www-project-' prefix.

        Returns:
            str: The normalized project key.
        """
        return self.key.replace("www-project-", "")

    @property
    def idx_languages(self) -> list[str]:
        """Return the programming languages for indexing.

        These languages represent the technologies used
        across the project's repositories.

        Returns:
            list[str]: A list of programming languages.
        """
        return self.languages

    @property
    def idx_level(self) -> str:
        """Return the project maturity level for indexing.

        This is the human-readable maturity level of the project.

        Returns:
            str: The project level.
        """
        return self.level

    @property
    def idx_level_raw(self) -> float | None:
        """Return the raw project level for indexing.

        This is the numeric representation of the project's
        maturity level.

        Returns:
            float | None: The raw project level, if available.
        """
        return float(self.level_raw) if self.level_raw else None

    @property
    def idx_name(self) -> str:
        """Return the project name for indexing.

        If a name is not explicitly set, a formatted name
        is derived from the project key.

        Returns:
            str: The project name.
        """
        return self.name or " ".join(self.key.replace("www-project-", "").capitalize().split("-"))

    @property
    def idx_organizations(self) -> str:
        """Return organization names for indexing.

        This aggregates the names of all organizations
        associated with the project.

        Returns:
            str: A concatenated string of organization names.
        """
        return join_values(fields=[o.name for o in self.organizations.all()])

    @property
    def idx_repositories(self) -> list[dict]:
        """Return project repositories for indexing.

        This returns a list of the top repositories associated
        with the project, ordered by star count, including
        key metadata for search display.

        Returns:
            list[dict]: A list of repository metadata dictionaries.
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
        """Return the number of repositories for indexing.

        This represents how many repositories are linked
        to the project.

        Returns:
            int: The repository count.
        """
        return self.repositories.count()

    @property
    def idx_stars_count(self) -> int:
        """Return the total star count for indexing.

        This represents the combined number of stars
        across the project's repositories.

        Returns:
            int: The star count.
        """
        return self.stars_count

    @property
    def idx_top_contributors(self) -> list:
        """Return the top contributors for indexing.

        This returns a list of the most active contributors
        across the project's repositories.

        Returns:
            list: A list of contributor data.
        """
        return RepositoryContributor.get_top_contributors(project=self.key)

    @property
    def idx_type(self) -> str:
        """Return the project type for indexing.

        This value categorizes the project within
        the OWASP ecosystem.

        Returns:
            str: The project type.
        """
        return self.type

    @property
    def idx_updated_at(self) -> str | float:
        """Return the last update timestamp for indexing.

        This represents when the project was last updated
        and is used for sorting and freshness indicators.

        Returns:
            str | float: The last update time as a Unix timestamp or an empty string.
        """
        return self.updated_at.timestamp() if self.updated_at else ""
