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
        """Indicate whether the repository should be indexed.

        A repository is considered indexable if it is not archived,
        not empty, not a template, and is associated with at least one
        OWASP project. This is used to decide whether the repository
        should be included in the search index.

        Returns:
            bool: True if the repository should be indexed, False otherwise.
        """
        return (
            not self.is_archived
            and not self.is_empty
            and not self.is_template
            and self.project_set.exists()
        )

    @property
    def idx_commits_count(self) -> int:
        """Return the number of commits for indexing.

        This value is used by the search index to represent the
        total number of commits in the repository.

        Returns:
            int: The commit count of the repository.
        """
        return self.commits_count

    @property
    def idx_contributors_count(self) -> int:
        """Return the number of contributors for indexing.

        This value represents how many contributors have
        contributed to the repository and is stored in the
        search index.

        Returns:
            int: The total number of contributors.
        """
        return self.contributors_count

    @property
    def idx_created_at(self) -> float:
        """Return the repository creation timestamp for indexing.

        The creation time is converted to a Unix timestamp and
        stored in the search index for sorting and filtering.

        Returns:
            float: The creation time as a Unix timestamp.
        """
        return self.created_at.timestamp()

    @property
    def idx_description(self) -> str:
        """Return the repository description for indexing.

        This value is used as the textual description of the
        repository in the search index.

        Returns:
            str: The repository description.
        """
        return self.description

    @property
    def idx_forks_count(self) -> int:
        """Return the number of forks for indexing.

        This value represents how many times the repository
        has been forked and is stored in the search index.

        Returns:
            int: The fork count of the repository.
        """
        return self.forks_count

    @property
    def idx_has_funding_yml(self) -> bool:
        """Return whether the repository has a funding.yml file.

        This indicates whether the repository has GitHub funding
        configuration and is included in the search index.

        Returns:
            bool: True if a funding.yml file exists, False otherwise.
        """
        return self.has_funding_yml

    @property
    def idx_key(self) -> str:
        """Return the unique Nest key for indexing.

        This key uniquely identifies the repository in the
        Nest platform and is used as the index key.

        Returns:
            str: The Nest key of the repository.
        """
        return self.nest_key

    @property
    def idx_languages(self) -> list[str]:
        """Return the programming languages used by the repository.

        These languages are indexed to allow filtering and
        searching by technology.

        Returns:
            list[str]: A list of programming languages used in the repository.
        """
        return self.languages

    @property
    def idx_license(self) -> str:
        """Return the repository license for indexing.

        This value represents the software license associated
        with the repository.

        Returns:
            str: The license name.
        """
        return self.license

    @property
    def idx_name(self) -> str:
        """Return the repository name for indexing.

        This value is used as the primary display name of the
        repository in the search index.

        Returns:
            str: The name of the repository.
        """
        return self.name

    @property
    def idx_open_issues_count(self) -> int:
        """Return the number of open issues for indexing.

        This value represents how many issues are currently
        open on the repository.

        Returns:
            int: The number of open issues.
        """
        return self.open_issues_count

    @property
    def idx_project_key(self) -> str:
        """Return the Nest project key associated with this repository.

        If the repository is linked to a project, its Nest key
        is returned. Otherwise, an empty string is used.

        Returns:
            str: The Nest key of the associated project, or an empty string.
        """
        return self.project.nest_key if self.project else ""

    @property
    def idx_pushed_at(self) -> float:
        """Return the last push timestamp for indexing.

        This represents when the repository was last updated
        and is stored as a Unix timestamp.

        Returns:
            float: The last push time as a Unix timestamp.
        """
        return self.pushed_at.timestamp()

    @property
    def idx_size(self) -> int:
        """Return the repository size for indexing.

        This value represents the size of the repository
        as reported by GitHub.

        Returns:
            int: The repository size.
        """
        return self.size

    @property
    def idx_stars_count(self) -> int:
        """Return the number of stars for indexing.

        This value represents how many GitHub users have starred
        the repository.

        Returns:
            int: The star count of the repository.
        """
        return self.stars_count

    @property
    def idx_subscribers_count(self) -> int:
        """Return the subscriber-related value used for indexing.

        This property currently returns the same value as the
        repository's star count and is indexed under the
        subscribers field.

        Returns:
            int: The value used for the subscribers count in the index.
        """
        return self.stars_count

    @property
    def idx_top_contributors(self) -> list[dict[str, Any]]:
        """Return the top contributors for indexing.

        This retrieves a list of the most active contributors
        to the repository for display and search purposes.

        Returns:
            list[dict[str, Any]]: A list of contributor metadata dictionaries.
        """
        return RepositoryContributor.get_top_contributors(repository=self.key)

    @property
    def idx_topics(self):
        """Return the repository topics for indexing.

        Topics are used as tags to improve discoverability
        in the search index.

        Returns:
            Any: The topics associated with the repository.
        """
        return self.topics
