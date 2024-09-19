"""GitHub issue mixins."""

from apps.github.constants import GITHUB_GHOST_USER_LOGIN


class IssueIndexMixin:
    """Issue index mixin."""

    @property
    def idx_author_login(self):
        """Return author login for indexing."""
        return (
            self.author.login
            if self.author and self.author.login and self.author.login != GITHUB_GHOST_USER_LOGIN
            else ""
        )

    @property
    def idx_author_name(self):
        """Return author name for indexing."""
        return (
            self.author.name
            if self.author and self.author.login != GITHUB_GHOST_USER_LOGIN
            else ""
        )

    @property
    def idx_comments_count(self):
        """Return comments count at for indexing."""
        return self.comments_count

    @property
    def idx_created_at(self):
        """Return created at for indexing."""
        return self.created_at

    @property
    def idx_hint(self):
        """Return hint for indexing."""
        return self.hint if self.hint else None

    @property
    def idx_labels(self):
        """Return labels for indexing."""
        return [label.name for label in self.labels.all()]

    @property
    def idx_project_description(self):
        """Return project description for indexing."""
        return self.project.idx_description if self.project else ""

    @property
    def idx_project_level(self):
        """Return project level for indexing."""
        return self.project.idx_level if self.project else ""

    @property
    def idx_project_tags(self):
        """Return project tags for indexing."""
        return self.project.idx_tags if self.project else []

    @property
    def idx_project_topics(self):
        """Return project topics for indexing."""
        return self.project.idx_topics if self.project else []

    @property
    def idx_project_name(self):
        """Return project name for indexing."""
        return self.project.idx_name if self.project else ""

    @property
    def idx_project_url(self):
        """Return project URL for indexing."""
        return self.project.idx_url if self.project else None

    @property
    def idx_repository_contributors_count(self):
        """Return repository contributors count for indexing."""
        return self.repository.idx_contributors_count

    @property
    def idx_repository_description(self):
        """Return repository description for indexing."""
        return self.repository.idx_description

    @property
    def idx_repository_forks_count(self):
        """Return repository forks count for indexing."""
        return self.repository.idx_forks_count

    @property
    def idx_repository_languages(self):
        """Return repository languages for indexing."""
        return self.repository.idx_languages

    @property
    def idx_repository_name(self):
        """Return repository name for indexing."""
        return self.repository.idx_name

    @property
    def idx_repository_stars_count(self):
        """Return repository stars count for indexing."""
        return self.repository.idx_stars_count

    @property
    def idx_summary(self):
        """Return summary for indexing."""
        return self.summary

    @property
    def idx_title(self):
        """Return title for indexing."""
        return self.title

    @property
    def idx_repository_topics(self):
        """Return repository stars count for indexing."""
        return self.repository.idx_topics

    @property
    def idx_updated_at(self):
        """Return updated at for indexing."""
        return self.updated_at

    @property
    def idx_url(self):
        """Return URL for indexing."""
        return self.url or None
