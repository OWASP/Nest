"""GitHub issue mixins."""

from __future__ import annotations


class IssueIndexMixin:
    """Issue index mixin for GitHub projects."""

    @property
    def is_indexable(self):
        """Return whether the issue should be indexed.

        Purpose:
            Determines if the issue is suitable for indexing:
            - must have an ID
            - must be open
            - not locked
            - repository is indexable and tracks issues
            - project exists and tracks issues
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

        Purpose:
            Provides the author's GitHub login for indexing and search.
        """
        return self.author.login if self.author else ""

    @property
    def idx_author_name(self) -> str:
        """Return author name for indexing.

        Purpose:
            Provides the author's display name for indexing.
        """
        return self.author.name if self.author else ""

    @property
    def idx_comments_count(self) -> int:
        """Return comments count for indexing.

        Purpose:
            Indicates the number of comments on the issue to improve search relevance.
        """
        return self.comments_count

    @property
    def idx_created_at(self) -> float:
        """Return creation timestamp for indexing.

        Purpose:
            Supplies the creation time of the issue for sorting and filtering.
        """
        return self.created_at.timestamp()

    @property
    def idx_hint(self) -> str:
        """Return hint for indexing.

        Purpose:
            Provides extra context or tips associated with the issue.
        """
        return self.hint

    @property
    def idx_labels(self) -> list[str]:
        """Return labels for indexing.

        Purpose:
            Lists issue labels to enhance search filtering and categorization.
        """
        return [label.name for label in self.labels.all()]

    @property
    def idx_project_description(self) -> str:
        """Return project description for indexing.

        Purpose:
            Provides the parent project's description to improve search context.
        """
        return self.project.idx_description if self.project else ""

    @property
    def idx_project_level(self) -> str:
        """Return project level for indexing.

        Purpose:
            Supplies the human-readable level of the project for filtering or sorting.
        """
        return self.project.idx_level if self.project else ""

    @property
    def idx_project_level_raw(self) -> str:
        """Return project raw level for indexing.

        Purpose:
            Supplies the numeric or raw level for precise sorting or indexing.
        """
        return self.project.idx_level_raw if self.project else ""

    @property
    def idx_project_tags(self) -> list[str]:
        """Return project tags for indexing.

        Purpose:
            Provides tags associated with the project to improve search relevance.
        """
        return self.project.idx_tags if self.project else []

    @property
    def idx_project_topics(self) -> list[str]:
        """Return project topics for indexing.

        Purpose:
            Lists topics of the project for better search categorization.
        """
        return self.project.idx_topics if self.project else []

    @property
    def idx_project_name(self) -> str:
        """Return project name for indexing.

        Purpose:
            Supplies the project name to establish context for the issue.
        """
        return self.project.idx_name if self.project else ""

    @property
    def idx_project_url(self) -> str:
        """Return project URL for indexing.

        Purpose:
            Provides a direct link to the parent project for reference.
        """
        return self.project.idx_url if self.project else ""

    @property
    def idx_repository_contributors_count(self) -> int:
        """Return repository contributors count for indexing.

        Purpose:
            Indicates the total contributors for repository-level relevance.
        """
        return self.repository.idx_contributors_count

    @property
    def idx_repository_description(self) -> str:
        """Return repository description for indexing.

        Purpose:
            Supplies repository context for issue indexing and search relevance.
        """
        return self.repository.idx_description

    @property
    def idx_repository_forks_count(self) -> int:
        """Return repository forks count for indexing.

        Purpose:
            Indicates repository popularity and relevance for search indexing.
        """
        return self.repository.idx_forks_count

    @property
    def idx_repository_languages(self) -> list[str]:
        """Return repository languages for indexing.

        Purpose:
            Lists the primary languages of the repository for filtering or categorization.
        """
        return self.repository.top_languages

    @property
    def idx_repository_name(self) -> str:
        """Return repository name for indexing.

        Purpose:
            Supplies the repository name to establish context for the issue.
        """
        return self.repository.idx_name

    @property
    def idx_repository_stars_count(self) -> int:
        """Return repository stars count for indexing.

        Purpose:
            Indicates popularity of the repository to improve search relevance.
        """
        return self.repository.idx_stars_count

    @property
    def idx_summary(self) -> str:
        """Return summary for indexing.

        Purpose:
            Provides a concise summary of the issue for search indexing.
        """
        return self.summary

    @property
    def idx_title(self) -> str:
        """Return title for indexing.

        Purpose:
            Supplies the issue title for search and indexing relevance.
        """
        return self.title

    @property
    def idx_repository_topics(self) -> list[str]:
        """Return repository topics for indexing.

        Purpose:
            Lists repository topics to enhance search filtering and categorization.
        """
        return self.repository.idx_topics

    @property
    def idx_updated_at(self) -> float:
        """Return updated timestamp for indexing.

        Purpose:
            Provides the last modification time for sorting and relevance.
        """
        return self.updated_at.timestamp()

    @property
    def idx_url(self) -> str:
        """Return issue URL for indexing.

        Purpose:
            Supplies the direct link to the issue for reference and indexing.
        """
        return self.url
