"""OWASP app project mixins."""

from __future__ import annotations

from django.conf import settings

from apps.common.utils import join_values
from apps.github.models.repository_contributor import RepositoryContributor
from apps.owasp.models.mixins.common import RepositoryBasedEntityModelMixin

ISSUES_LIMIT = 6
RELEASES_LIMIT = 4
REPOSITORIES_LIMIT = 4


class ProjectIndexMixin(RepositoryBasedEntityModelMixin):
    """Project index mixin providing properties for indexing project data."""

    @property
    def idx_companies(self) -> str:
        """
        Returns a string of all associated companies.

        Purpose: Provides metadata for search indexing and filtering by companies.
        """
        return join_values(fields=[o.company for o in self.organizations.all()])

    @property
    def idx_contributors_count(self) -> int:
        """
        Returns the total number of contributors to the project.

        Purpose: Provides a metric of project activity for indexing.
        """
        return self.contributors_count

    @property
    def idx_custom_tags(self) -> str:
        """
        Returns custom tags associated with the project.

        Purpose: Supports search indexing and filtering based on tags.
        """
        return self.custom_tags

    @property
    def idx_forks_count(self) -> int:
        """
        Returns the number of forks of the project's repositories.

        Purpose: Indicates popularity and engagement for indexing.
        """
        return self.forks_count

    @property
    def idx_health_score(self) -> float | None:
        """
        Returns the health score of the project.

        Purpose: Provides an indicator of project quality or activity.
        Notes: Returns 100 in production environment as a placeholder.
        """
        # TODO: Enable real health score in production when ready.
        return 100 if settings.IS_PRODUCTION_ENVIRONMENT else self.health_score

    @property
    def idx_is_active(self) -> bool:
        """
        Returns whether the project is active.

        Purpose: Helps filter and index only active projects.
        """
        return self.is_active

    @property
    def idx_issues_count(self) -> int:
        """
        Returns the total number of open issues for the project.

        Purpose: Provides project activity metric for indexing.
        """
        return self.open_issues.count()

    @property
    def idx_key(self) -> str:
        """
        Returns the project's key for indexing.

        Purpose: Provides a unique identifier for search and linking.
        """
        return self.key.replace("www-project-", "")

    @property
    def idx_languages(self) -> list[str]:
        """
        Returns the list of programming languages used in the project.

        Purpose: Supports language-based filtering and indexing.
        """
        return self.languages

    @property
    def idx_level(self) -> str:
        """
        Returns the level of the project as a string.

        Purpose: Provides human-readable project level metadata for indexing.
        """
        return self.level

    @property
    def idx_level_raw(self) -> float | None:
        """
        Returns the numeric level of the project.

        Purpose: Supports quantitative indexing or sorting by project level.
        """
        return float(self.level_raw) if self.level_raw else None

    @property
    def idx_name(self) -> str:
        """
        Returns the project's name.

        Purpose: Provides display and search metadata for indexing.
        Notes: Defaults to formatted key if name is missing.
        """
        return self.name or " ".join(self.key.replace("www-project-", "").capitalize().split("-"))

    @property
    def idx_organizations(self) -> str:
        """
        Returns a string of all associated organizations.

        Purpose: Supports search indexing and filtering by organizations.
        """
        return join_values(fields=[o.name for o in self.organizations.all()])

    @property
    def idx_repositories(self) -> list[dict]:
        """
        Returns a list of repositories with key metadata for indexing.

        Purpose: Provides detailed repository info including contributors, 
        description, forks, latest release, license, owner, and stars count.
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
        """
        Returns the total number of repositories in the project.

        Purpose: Provides project activity metric for indexing.
        """
        return self.repositories.count()

    @property
    def idx_stars_count(self) -> int:
        """
        Returns the total number of stars across the project's repositories.

        Purpose: Indicates popularity and engagement for indexing.
        """
        return self.stars_count

    @property
    def idx_top_contributors(self) -> list:
        """
        Returns a list of top contributors for the project.

        Purpose: Provides contributor metadata for indexing and ranking.
        """
        return RepositoryContributor.get_top_contributors(project=self.key)

    @property
    def idx_type(self) -> str:
        """
        Returns the project type.

        Purpose: Supports type-based filtering and indexing.
        """
        return self.type

    @property
    def idx_updated_at(self) -> str | float:
        """
        Returns the timestamp of the last project update.

        Purpose: Useful for sorting and indexing by recent activity.
        Returns empty string if updated_at is not set.
        """
        return self.updated_at.timestamp() if self.updated_at else ""
