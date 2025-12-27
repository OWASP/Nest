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
            bool: True if the repository meets indexing criteria, False otherwise.

        """
        return (
            not self.is_archived
            and not self.is_empty
            and not self.is_template
            and self.project_set.exists()
        )

    @property
    def idx_commits_count(self) -> int:
        """Return commits count for indexing.

        Returns:
            int: The total number of commits in the repository.

        """
        return self.commits_count

    @property
    def idx_contributors_count(self) -> int:
        """Return contributors count for indexing.

        Returns:
            int: The number of contributors to the repository.

        """
        return self.contributors_count

    @property
    def idx_created_at(self) -> float:
        """Return created at timestamp for indexing.

        Returns:
            float: The repository creation timestamp.

        """
        return self.created_at.timestamp()

    @property
    def idx_description(self) -> str:
        """Return description for indexing.

        Returns:
            str: The repository description.

        """
        return self.description

    @property
    def idx_forks_count(self) -> int:
        """Return forks count for indexing.

        Returns:
            int: The number of forks of the repository.

        """
        return self.forks_count

    @property
    def idx_has_funding_yml(self) -> bool:
        """Return whether repository has funding.yml for indexing.

        Returns:
            bool: True if the repository has a funding.yml file, False otherwise.

        """
        return self.has_funding_yml

    @property
    def idx_key(self) -> str:
        """Return key for indexing.

        Returns:
            str: The nest key of the repository.

        """
        return self.nest_key

    @property
    def idx_languages(self) -> list[str]:
        """Return languages for indexing.

        Returns:
            list[str]: A list of programming languages used in the repository.

        """
        return self.languages

    @property
    def idx_license(self) -> str:
        """Return license for indexing.

        Returns:
            str: The license of the repository.

        """
        return self.license

    @property
    def idx_name(self) -> str:
        """Return name for indexing.

        Returns:
            str: The name of the repository.

        """
        return self.name

    @property
    def idx_open_issues_count(self) -> int:
        """Return open issues count for indexing.

        Returns:
            int: The number of open issues in the repository.

        """
        return self.open_issues_count

    @property
    def idx_project_key(self) -> str:
        """Return project key for indexing.

        Returns:
            str: The nest key of the associated project, or empty string.

        """
        return self.project.nest_key if self.project else ""

    @property
    def idx_pushed_at(self) -> float:
        """Return pushed at timestamp for indexing.

        Returns:
            float: The last push timestamp of the repository.

        """
        return self.pushed_at.timestamp()

    @property
    def idx_size(self) -> int:
        """Return size for indexing.

        Returns:
            int: The size of the repository in kilobytes.

        """
        return self.size

    @property
    def idx_stars_count(self) -> int:
        """Return stars count for indexing.

        Returns:
            int: The number of stars the repository has received.

        """
        return self.stars_count

    @property
    def idx_subscribers_count(self) -> int:
        """Return subscribers count for indexing.

        Returns:
            int: The number of subscribers to the repository.

        """
        return self.subscribers_count 

    @property
    def idx_top_contributors(self) -> list[dict[str, Any]]:
        """Return top contributors for indexing.

        Returns:
            list[dict[str, Any]]: A list of top contributor details.

        """
        return RepositoryContributor.get_top_contributors(repository=self.key)

    @property
    def idx_topics(self):
        """Return topics for indexing.

        Returns:
            list[str]: A list of topics associated with the repository.

        """
        return self.topics
