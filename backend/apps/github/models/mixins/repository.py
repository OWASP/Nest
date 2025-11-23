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
        """
        Return: bool — True when repository should be indexed.

        Purpose:
            Indicates whether this repository meets the conditions to be indexed
            (not archived, not empty, not a template, and linked to a project).
        """
        return (
            not self.is_archived
            and not self.is_empty
            and not self.is_template
            and self.project_set.exists()
        )

    @property
    def idx_commits_count(self) -> int:
        """
        Return: int — number of commits (e.g. 123).

        Purpose:
            Exposes the commit count used by the search/indexing system.
        """
        return self.commits_count

    @property
    def idx_contributors_count(self) -> int:
        """
        Return: int — number of contributors (e.g. 12).

        Purpose:
            Provides the contributor count for indexing and ranking.
        """
        return self.contributors_count

    @property
    def idx_created_at(self) -> float:
        """
        Return: float — UNIX timestamp of repository creation (seconds since epoch).

        Purpose:
            Provides a numeric creation time suitable for sorting or range queries in the index.
        """
        return self.created_at.timestamp()

    @property
    def idx_description(self) -> str:
        """
        Return: str — repository description (short string).

        Purpose:
            Supplies the textual description used by full-text indexing and search results.
        """
        return self.description

    @property
    def idx_forks_count(self) -> int:
        """
        Return: int — forks count (e.g. 42).

        Purpose:
            Exposes repository fork count for indexing and popularity metrics.
        """
        return self.forks_count

    @property
    def idx_has_funding_yml(self) -> bool:
        """
        Return: bool — True if repository contains a FUNDING.yml file.

        Purpose:
            Signals whether funding metadata is present, used for filtering and indexing.
        """
        return self.has_funding_yml

    @property
    def idx_key(self) -> str:
        """
        Return: str — canonical nest key for this repository (unique identifier).

        Purpose:
            Provides the unique key used by the indexing system to identify this repository.
        """
        return self.nest_key

    @property
    def idx_languages(self) -> list[str]:
        """
        Return: list[str] — list of languages used in the repository (e.g. ['Python', 'HTML']).

        Purpose:
            Supplies languages for language-based filtering and search facets.
        """
        return self.languages

    @property
    def idx_license(self) -> str | None:
        """
        Return: Optional[str] — license name (e.g. 'MIT') or None if unspecified.

        Purpose:
            Exposes license information for display and index-driven license filtering.
        """
        return self.license

    @property
    def idx_name(self) -> str:
        """
        Return: str — repository name (e.g. 'awesome-project').

        Purpose:
            Supplies the repository name used in index records and search hits.
        """
        return self.name

    @property
    def idx_open_issues_count(self) -> int:
        """
        Return: int — number of open issues (e.g. 5).

        Purpose:
            Exposes open issue count used for ranking and filtering in the index.
        """
        return self.open_issues_count

    @property
    def idx_project_key(self) -> str:
        """
        Return: str — associated project nest key, or empty string when not linked.

        Purpose:
            Links this repository's index record to a higher-level project if available.
        """
        return self.project.nest_key if self.project else ""

    @property
    def idx_pushed_at(self) -> float:
        """
        Return: float — UNIX timestamp of the repository's last push (seconds since epoch).

        Purpose:
            Used to determine recency for search ranking and incremental indexing.
        """
        return self.pushed_at.timestamp()

    @property
    def idx_size(self) -> int:
        """
        Return: int — repository size (in KB as reported by GitHub, typically).

        Purpose:
            Exposes repository size for informational display and potential sizing filters.
        """
        return self.size

    @property
    def idx_stars_count(self) -> int:
        """
        Return: int — number of stars (e.g. 150).

        Purpose:
            Supplies star count used as a popularity signal in indexing and ranking.
        """
        return self.stars_count

    @property
    def idx_subscribers_count(self) -> int:
        """
        Return: int — number of subscribers/watchers (e.g. 20).

        Purpose:
            Exposes subscriber/watch count used as an engagement signal for indexing.
        """
        return self.subscribers_count

    @property
    def idx_top_contributors(self) -> list[dict[str, Any]]:
        """
        Return: list[dict] — top contributor entries, each dict containing contributor info.

        Purpose:
            Returns structured top-contributor data used by the index to show contributor metadata.
        """
        return RepositoryContributor.get_top_contributors(repository=self.key)

    @property
    def idx_topics(self) -> list[str]:
        """
        Return: list[str] — repository topics/tags (e.g. ['security', 'owasp']).

        Purpose:
            Supplies repository topics used for tag-based search and filtering in the index.
        """
        return self.topics
