"""GitHub repository mixins."""

from __future__ import annotations

from typing import Any

from apps.github.models.repository_contributor import (
    RepositoryContributor,
)


class RepositoryIndexMixin:
    """Repository index mixin providing properties for indexing repository data."""

    @property
    def is_indexable(self) -> bool:
        """
        Returns whether the repository should be indexed.

        Purpose: Determines if the repository is eligible for search indexing,
        considering conditions like being archived, empty, a template, or lacking
        an associated project.
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
        Returns the total number of commits in the repository.

        Purpose: Provides a metric of repository activity for search indexing.
        """
        return self.commits_count

    @property
    def idx_contributors_count(self) -> int:
        """
        Returns the number of contributors to the repository.

        Purpose: Helps measure repository popularity and engagement for indexing.
        """
        return self.contributors_count

    @property
    def idx_created_at(self) -> float:
        """
        Returns the repository creation timestamp.

        Purpose: Useful for sorting and indexing repositories by creation date.
        """
        return self.created_at.timestamp()

    @property
    def idx_description(self) -> str:
        """
        Returns the repository description.

        Purpose: Provides textual metadata for search indexing or display.
        """
        return self.description

    @property
    def idx_forks_count(self) -> int:
        """
        Returns the number of times the repository has been forked.

        Purpose: Indicates repository popularity and helps with ranking in search.
        """
        return self.forks_count

    @property
    def idx_has_funding_yml(self) -> bool:
        """
        Returns True if the repository contains a FUNDING.yml file, False otherwise.

        Purpose: Used to identify repositories that support funding or sponsorships.
        """
        return self.has_funding_yml

    @property
    def idx_key(self) -> str:
        """
        Returns the repository's unique key (nest key).

        Purpose: Provides a unique identifier for indexing and linking repositories.
        """
        return self.nest_key

    @property
    def idx_languages(self) -> list[str]:
        """
        Returns a list of programming languages used in the repository.

        Purpose: Enables language-based indexing and filtering of repositories.
        """
        return self.languages

    @property
    def idx_license(self) -> str:
        """
        Returns the license type of the repository.

        Purpose: Allows filtering and indexing of repositories by license type.
        """
        return self.license

    @property
    def idx_name(self) -> str:
        """
        Returns the name of the repository.

        Purpose: Provides an identifier for search indexing and display purposes.
        """
        return self.name

    @property
    def idx_open_issues_count(self) -> int:
        """
        Returns the number of open issues in the repository.

        Purpose: Provides activity metrics for indexing and analytics.
        """
        return self.open_issues_count

    @property
    def idx_project_key(self) -> str:
        """
        Returns the nest key of the associated project, or an empty string if none exists.

        Purpose: Provides project linkage information for indexing purposes.
        """
        return self.project.nest_key if self.project else ""

    @property
    def idx_pushed_at(self) -> float:
        """
        Returns the timestamp of the last push to the repository.

        Purpose: Useful for indexing and sorting repositories by recent activity.
        """
        return self.pushed_at.timestamp()

    @property
    def idx_size(self) -> int:
        """
        Returns the size of the repository in kilobytes.

        Purpose: Useful for filtering and indexing repositories by size.
        """
        return self.size

    @property
    def idx_stars_count(self) -> int:
        """
        Returns the number of stars on the repository.

        Purpose: Indicates repository popularity for indexing and ranking.
        """
        return self.stars_count

    @property
    def idx_subscribers_count(self) -> int:
        """
        Returns the number of subscribers/watchers of the repository.

        Purpose: Helps measure community engagement and repository popularity.
        """
        return self.stars_count

    @property
    def idx_top_contributors(self) -> list[dict[str, Any]]:
        """
        Returns a list of top contributors for the repository.

        Purpose: Provides information about the most active contributors
        for indexing or display. Each contributor is represented as a dictionary
        containing their login and contribution count.
        """
        return RepositoryContributor.get_top_contributors(repository=self.key)

    @property
    def idx_topics(self) -> list[str]:
        """
        Returns the list of topics or tags associated with the repository.

        Purpose: Enables topic-based search and categorization of repositories.
        """
        return self.topics
