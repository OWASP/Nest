"""GitHub issue mixins."""

from __future__ import annotations


class IssueIndexMixin:
    """Issue index mixin."""

    @property
    def is_indexable(self):
        """Determine if the issue should be indexed.

        Returns:
            bool: True if the issue meets indexing criteria, False otherwise.

        """
        return (
            self.id
            and self.state == self.State.OPEN
            and not self.is_locked
            and self.repository.is_indexable
            and self.repository.track_issues
            and self.project
            and self.project.track_issues
        )

    @property
    def idx_author_login(self) -> str:
        """Return author login for indexing.

        Returns:
            str: The login name of the issue author.

        """
        return self.author.login if self.author else ""

    @property
    def idx_author_name(self) -> str:
        """Return author name for indexing.

        Returns:
            str: The name of the issue author.

        """
        return self.author.name if self.author else ""

    @property
    def idx_comments_count(self) -> int:
        """Return comments count for indexing.

        Returns:
            int: The number of comments on the issue.

        """
        return self.comments_count

    @property
    def idx_created_at(self) -> float:
        """Return created at timestamp for indexing.

        Returns:
            float: The issue creation timestamp.

        """
        return self.created_at.timestamp()

    @property
    def idx_hint(self) -> str:
        """Return hint for indexing.

        Returns:
            str: The hint associated with the issue.

        """
        return self.hint

    @property
    def idx_labels(self) -> list[str]:
        """Return labels for indexing.

        Returns:
            list[str]: A list of label names on the issue.

        """
        return [label.name for label in self.labels.all()]

    @property
    def idx_project_description(self) -> str:
        """Return project description for indexing.

        Returns:
            str: The description of the associated project.

        """
        return self.project.idx_description if self.project else ""

    @property
    def idx_project_level(self) -> str:
        """Return project level for indexing.

        Returns:
            str: The level of the associated project.

        """
        return self.project.idx_level if self.project else ""

    @property
    def idx_project_level_raw(self) -> str:
        """Return project raw level for indexing.

        Returns:
            str: The raw level of the associated project.

        """
        return self.project.idx_level_raw if self.project else ""

    @property
    def idx_project_tags(self) -> list[str]:
        """Return project tags for indexing.

        Returns:
            list[str]: A list of tags from the associated project.

        """
        return self.project.idx_tags if self.project else []

    @property
    def idx_project_topics(self) -> list[str]:
        """Return project topics for indexing.

        Returns:
            list[str]: A list of topics from the associated project.

        """
        return self.project.idx_topics if self.project else []

    @property
    def idx_project_name(self) -> str:
        """Return project name for indexing.

        Returns:
            str: The name of the associated project.

        """
        return self.project.idx_name if self.project else ""

    @property
    def idx_project_url(self) -> str:
        """Return project URL for indexing.

        Returns:
            str: The URL of the associated project.

        """
        return self.project.idx_url if self.project else ""

    @property
    def idx_repository_contributors_count(self) -> int:
        """Return repository contributors count for indexing.

        Returns:
            int: The number of contributors to the repository.

        """
        return self.repository.idx_contributors_count

    @property
    def idx_repository_description(self) -> str:
        """Return repository description for indexing.

        Returns:
            str: The description of the repository.

        """
        return self.repository.idx_description

    @property
    def idx_repository_forks_count(self) -> int:
        """Return repository forks count for indexing.

        Returns:
            int: The number of repository forks.

        """
        return self.repository.idx_forks_count

    @property
    def idx_repository_languages(self) -> list[str]:
        """Return repository languages for indexing.

        Returns:
            list[str]: A list of top languages in the repository.

        """
        return self.repository.top_languages

    @property
    def idx_repository_name(self) -> str:
        """Return repository name for indexing.

        Returns:
            str: The name of the repository.

        """
        return self.repository.idx_name

    @property
    def idx_repository_stars_count(self) -> int:
        """Return repository stars count for indexing.

        Returns:
            int: The number of stars the repository has.

        """
        return self.repository.idx_stars_count

    @property
    def idx_summary(self) -> str:
        """Return summary for indexing.

        Returns:
            str: The summary of the issue.

        """
        return self.summary

    @property
    def idx_title(self) -> str:
        """Return title for indexing.

        Returns:
            str: The title of the issue.

        """
        return self.title

    @property
    def idx_repository_topics(self) -> list[str]:
        """Return repository topics for indexing.

        Returns:
            list[str]: A list of topics from the repository.

        """
        return self.repository.idx_topics

    @property
    def idx_updated_at(self) -> float:
        """Return updated at timestamp for indexing.

        Returns:
            float: The issue's last update timestamp.

        """
        return self.updated_at.timestamp()

    @property
    def idx_url(self) -> str:
        """Return URL for indexing.

        Returns:
            str: The URL of the issue.

        """
        return self.url
