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
        """Determine if the repository should be indexed.

        Returns:
            bool: True if repository meets all indexing criteria, False otherwise.

        """
        return (
            not self.is_archived
            and not self.is_empty
            and not self.is_template
            and self.project_set.exists()
        )

    @property
    def idx_commits_count(self) -> int:
        """Get the total number of commits in this repository for indexing.

        Returns:
            int: The total commit count of the repository.

        """
        return self.commits_count

    @property
    def idx_contributors_count(self) -> int:
        """Get the total number of contributors to this repository for indexing.

        Returns:
            int: The total number of unique contributors.

        """
        return self.contributors_count

    @property
    def idx_created_at(self) -> float:
        """Get the repository creation timestamp for indexing.

        Returns:
            float: Unix timestamp when the repository was created.

        """
        return self.created_at.timestamp()

    @property
    def idx_description(self) -> str:
        """Get the repository description for indexing.

        Returns:
            str: The repository's description text.

        """
        return self.description

    @property
    def idx_forks_count(self) -> int:
        """Get the total number of repository forks for indexing.

        Returns:
            int: The total number of times this repository has been forked.

        """
        return self.forks_count

    @property
    def idx_has_funding_yml(self) -> bool:
        """Check if the repository has a FUNDING.yml file for indexing.

        Returns:
            bool: True if the repository contains a FUNDING.yml file, False otherwise.

        """
        return self.has_funding_yml

    @property
    def idx_key(self) -> str:
        """Get the unique Nest key identifier for this repository for indexing.

        Returns:
            str: The repository's unique Nest key.

        """
        return self.nest_key

    @property
    def idx_languages(self) -> list[str]:
        """Get the programming languages used in this repository for indexing.

        Returns:
            list[str]: A list of programming language names detected in the repository.

        """
        return self.languages

    @property
    def idx_license(self) -> str:
        """Get the repository's license identifier for indexing.

        Returns:
            str: The license identifier.

        """
        return self.license

    @property
    def idx_name(self) -> str:
        """Get the repository name for indexing.

        Returns:
            str: The name of the repository.

        """
        return self.name

    @property
    def idx_open_issues_count(self) -> int:
        """Get the total number of open issues in this repository for indexing.

        Returns:
            int: The count of currently open issues.

        """
        return self.open_issues_count

    @property
    def idx_project_key(self) -> str:
        """Get the Nest key of the associated project for indexing.

        Returns:
            str: The unique Nest key of the project this repository belongs to,
                or an empty string if no project is associated.

        """
        return self.project.nest_key if self.project else ""

    @property
    def idx_pushed_at(self) -> float:
        """Get the timestamp of the last push to this repository for indexing.

        Returns:
            float: Unix timestamp of the most recent push.

        """
        return self.pushed_at.timestamp()

    @property
    def idx_size(self) -> int:
        """Get the repository size in kilobytes for indexing.

        Returns:
            int: The repository size in KB.

        """
        return self.size

    @property
    def idx_stars_count(self) -> int:
        """Get the total number of stars this repository has received for indexing.

        Returns:
            int: The total count of stars on the repository.

        """
        return self.stars_count

    @property
    def idx_subscribers_count(self) -> int:
        """Get the total number of subscribers for this repository for indexing.

        Returns:
            int: The count of users watching this repository.

        """
        return self.subscribers_count

    @property
    def idx_top_contributors(self) -> list[dict[str, Any]]:
        """Get the list of top contributors to this repository for indexing.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing information about
                the top contributors to this repository.

        """
        return RepositoryContributor.get_top_contributors(repository=self.key)

    @property
    def idx_topics(self) -> list[str]:
        """Get the topics associated with this repository for indexing.

        Returns:
            list: A list of topics that categorize this repository.

        """
        return self.topics
