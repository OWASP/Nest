"""GitHub issue mixins."""

from __future__ import annotations


class IssueIndexMixin:
    """Issue index mixin."""

    @property
    def is_indexable(self):
        """Issues to index."""
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
        """Return author login for indexing."""
        return self.author.login if self.author else ""

    @property
    def idx_author_name(self) -> str:
        """Return author name for indexing."""
        return self.author.name if self.author else ""

    @property
    def idx_comments_count(self) -> int:
        """Return comments count at for indexing."""
        return self.comments_count

    @property
    def idx_created_at(self) -> float:
        """Return created at for indexing."""
        return self.created_at.timestamp()

    @property
    def idx_hint(self) -> str:
        """Return hint for indexing."""
        return self.hint

    @property
    def idx_labels(self) -> list[str]:
        """Return labels for indexing."""
        return [label.name for label in self.labels.all()]

    @property
    def idx_project_description(self) -> str:
        """Return project description for indexing."""
        return self.project.idx_description if self.project else ""

    @property
    def idx_project_level(self) -> str:
        """Return project level or indexing."""
        return self.project.idx_level if self.project else ""

    @property
    def idx_project_level_raw(self) -> str:
        """Return project raw level for indexing."""
        return self.project.idx_level_raw if self.project else ""

    @property
    def idx_project_tags(self) -> list[str]:
        """Return project tags for indexing."""
        return self.project.idx_tags if self.project else []

    @property
    def idx_tags(self) -> list[str]:
        """Return tags for indexing (from project)."""
        return self.project.idx_tags if self.project else []

    @property
    def idx_project_topics(self) -> list[str]:
        """Return project topics for indexing."""
        return self.project.idx_topics if self.project else []

    @property
    def idx_project_name(self) -> str:
        """Return project name for indexing."""
        return self.project.idx_name if self.project else ""

    @property
    def idx_project_url(self) -> str:
        """Return project URL for indexing."""
        return self.project.idx_url if self.project else ""

    @property
    def idx_repository_contributors_count(self) -> int:
        """Return repository contributors count for indexing."""
        return self.repository.idx_contributors_count

    @property
    def idx_repository_description(self) -> str:
        """Return repository description for indexing."""
        return self.repository.idx_description

    @property
    def idx_repository_forks_count(self) -> int:
        """Return repository forks count for indexing."""
        return self.repository.idx_forks_count

    @property
    def idx_repository_languages(self) -> list[str]:
        """Return repository languages for indexing."""
        return self.repository.top_languages

    @property
    def idx_repository_name(self) -> str:
        """Return repository name for indexing."""
        return self.repository.idx_name

    @property
    def idx_repository_stars_count(self) -> int:
        """Return repository stars count for indexing."""
        return self.repository.idx_stars_count

    @property
    def idx_summary(self) -> str:
        """Return summary for indexing."""
        return self.summary

    @property
    def idx_title(self) -> str:
        """Return title for indexing."""
        return self.title

    @property
    def idx_repository_topics(self) -> list[str]:
        """Return repository stars count for indexing."""
        return self.repository.idx_topics

    @property
    def idx_updated_at(self) -> float:
        """Return updated at for indexing."""
        return self.updated_at.timestamp()

    @property
    def idx_url(self) -> str:
        """Return URL for indexing."""
        return self.url
