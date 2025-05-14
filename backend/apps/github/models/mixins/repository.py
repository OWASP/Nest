"""GitHub repository mixins."""

from __future__ import annotations

from typing import Any

from apps.github.models.repository_contributor import (
    RepositoryContributor,
)


class RepositoryIndexMixin:
    """Repository index mixin."""

    @property
    def is_indexable(self) -> bool:
        """Repositories to index."""
        return (
            not self.is_archived
            and not self.is_empty
            and not self.is_template
            and self.project_set.exists()
        )

    @property
    def idx_commits_count(self) -> int:
        """Return commits count for indexing."""
        return self.commits_count

    @property
    def idx_contributors_count(self) -> int:
        """Return contributors count for indexing."""
        return self.contributors_count

    @property
    def idx_created_at(self) -> float:
        """Return created at for indexing."""
        return self.created_at.timestamp()

    @property
    def idx_description(self) -> str:
        """Return description for indexing."""
        return self.description

    @property
    def idx_forks_count(self) -> int:
        """Return forks count for indexing."""
        return self.forks_count

    @property
    def idx_has_funding_yml(self) -> bool:
        """Return has funding.yml for indexing."""
        return self.has_funding_yml

    @property
    def idx_key(self) -> str:
        """Return key for indexing."""
        return self.nest_key

    @property
    def idx_languages(self) -> list[str]:
        """Return languages for indexing."""
        return self.languages

    @property
    def idx_license(self) -> str:
        """Return license for indexing."""
        return self.license

    @property
    def idx_name(self) -> str:
        """Return name for indexing."""
        return self.name

    @property
    def idx_open_issues_count(self) -> int:
        """Return open issues count for indexing."""
        return self.open_issues_count

    @property
    def idx_project_key(self) -> str:
        """Return project key for indexing."""
        return self.project.nest_key if self.project else ""

    @property
    def idx_pushed_at(self) -> float:
        """Return pushed at for indexing."""
        return self.pushed_at.timestamp()

    @property
    def idx_size(self) -> int:
        """Return size for indexing."""
        return self.size

    @property
    def idx_stars_count(self) -> int:
        """Return stars count for indexing."""
        return self.stars_count

    @property
    def idx_subscribers_count(self) -> int:
        """Return subscribers count for indexing."""
        return self.stars_count

    @property
    def idx_top_contributors(self) -> list[dict[str, Any]]:
        """Return top contributors for indexing."""
        return RepositoryContributor.get_top_contributors(repository=self.key)

    @property
    def idx_topics(self):
        """Return topics for indexing."""
        return self.topics
