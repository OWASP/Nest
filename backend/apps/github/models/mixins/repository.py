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
        """Determine if the repository is indexable.

        Returns:
            bool: True if not archived, not empty, not a template, and belongs to a project; False otherwise.
        """
        return (
            not self.is_archived
            and not self.is_empty
            and not self.is_template
            and self.project_set.exists()
        )

    @property
    def idx_commits_count(self) -> int:
        """Return the commits count for indexing.

        Returns:
            int: The total number of commits in the repository.
        """
        return self.commits_count

    @property
    def idx_contributors_count(self) -> int:
        """Return the contributors count for indexing.

        Returns:
            int: The number of contributors to the repository.
        """
        return self.contributors_count

    @property
    def idx_created_at(self) -> float:
        """Return the created at timestamp for indexing.

        Returns:
            float: The creation timestamp of the repository.
        """
        return self.created_at.timestamp()

    @property
    def idx_description(self) -> str:
        """Return the description for indexing.

        Returns:
            str: The description of the repository.
        """
        return self.description

    @property
    def idx_forks_count(self) -> int:
        """Return the forks count for indexing.

        Returns:
            int: The number of forks of the repository.
        """
        return self.forks_count

    @property
    def idx_has_funding_yml(self) -> bool:
        """Return whether the repository has a funding.yml file for indexing.

        Returns:
            bool: True if the repository has a funding.yml file, False otherwise.
        """
        return self.has_funding_yml

    @property
    def idx_key(self) -> str:
        """Return the nest key for indexing.

        Returns:
            str: The nest key of the repository.
        """
        return self.nest_key

    @property
    def idx_languages(self) -> list[str]:
        """Return the languages for indexing.

        Returns:
            list[str]: A list of languages used in the repository.
        """
        return self.languages

    @property
    def idx_license(self) -> str:
        """Return the license for indexing.

        Returns:
            str: The license of the repository.
        """
        return self.license

    @property
    def idx_name(self) -> str:
        """Return the name for indexing.

        Returns:
            str: The name of the repository.
        """
        return self.name

    @property
    def idx_open_issues_count(self) -> int:
        """Return the open issues count for indexing.

        Returns:
            int: The number of open issues in the repository.
        """
        return self.open_issues_count

    @property
    def idx_project_key(self) -> str:
        """Return the project nest key for indexing.

        Returns:
            str: The nest key of the associated project, or an empty string.
        """
        return self.project.nest_key if self.project else ""

    @property
    def idx_pushed_at(self) -> float:
        """Return the pushed at timestamp for indexing.

        Returns:
            float: The last push timestamp of the repository.
        """
        return self.pushed_at.timestamp()

    @property
    def idx_size(self) -> int:
        """Return the size for indexing.

        Returns:
            int: The size of the repository.
        """
        return self.size

    @property
    def idx_stars_count(self) -> int:
        """Return the stars count for indexing.

        Returns:
            int: The number of stars received by the repository.
        """
        return self.stars_count

    @property
    def idx_subscribers_count(self) -> int:
        """Return the subscribers count for indexing.

        Returns:
            int: The number of subscribers to the repository.
        """
        return self.stars_count

    @property
    def idx_top_contributors(self) -> list[dict[str, Any]]:
        """Return the top contributors for indexing.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing top contributor details.
        """
        return RepositoryContributor.get_top_contributors(repository=self.key)

    @property
    def idx_topics(self):
        """Return the topics for indexing.

        Returns:
            list[str]: A list of topics associated with the repository.
        """
        return self.topics
