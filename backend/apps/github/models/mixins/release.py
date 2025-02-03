"""GitHub release model mixins for index-related functionality."""

from django.utils.text import Truncator


class ReleaseIndexMixin:
    """Release index mixin."""

    @property
    def is_indexable(self):
        """Releases to index."""
        return not self.is_draft

    @property
    def idx_author(self):
        """Return author for indexing."""
        """Get top contributors."""
        return (
            [
                {
                    "avatar_url": self.author.avatar_url,
                    "login": self.author.login,
                    "name": self.author.name,
                }
            ]
            if self.author
            else []
        )

    @property
    def idx_created_at(self):
        """Return created at timestamp for indexing."""
        return self.created_at.timestamp()

    @property
    def idx_description(self):
        """Return description for indexing."""
        return Truncator(self.description).chars(1000, truncate="...")

    @property
    def idx_is_pre_release(self):
        """Return is pre release count for indexing."""
        return self.is_pre_release

    @property
    def idx_name(self):
        """Return name for indexing."""
        return self.name

    @property
    def idx_project(self):
        """Return project for indexing."""
        return self.repository.project.nest_key if self.repository.project else ""

    @property
    def idx_published_at(self):
        """Return published at timestamp for indexing."""
        return self.published_at.timestamp() if self.published_at else None

    @property
    def idx_repository(self):
        """Return repository for indexing."""
        return self.repository.path.lower()

    @property
    def idx_tag_name(self):
        """Return tag name for indexing."""
        return self.tag_name
