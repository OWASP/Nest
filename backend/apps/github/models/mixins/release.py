"""GitHub release model mixins for index-related functionality."""

from __future__ import annotations

from apps.common.utils import truncate

DESCRIPTION_MAX_LENGTH = 1000


class ReleaseIndexMixin:
    """Release index mixin."""

    @property
    def is_indexable(self) -> bool:
        """Releases to index."""
        return not self.is_draft

    @property
    def idx_author(self) -> list[dict[str, str]]:
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
    def idx_created_at(self) -> float:
        """Return created at timestamp for indexing."""
        return self.created_at.timestamp()

    @property
    def idx_description(self) -> str:
        """Return description for indexing."""
        return truncate(self.description, 1000, truncate="...")
        return truncate(self.description, limit=DESCRIPTION_MAX_LENGTH)

    @property
    def idx_is_pre_release(self) -> bool:
        """Return is pre release count for indexing."""
        return self.is_pre_release

    @property
    def idx_name(self) -> str:
        """Return name for indexing."""
        return self.name

    @property
    def idx_project(self) -> str:
        """Return project for indexing."""
        return self.repository.project.nest_key if self.repository.project else ""

    @property
    def idx_published_at(self) -> float | None:
        """Return published at timestamp for indexing."""
        return self.published_at.timestamp() if self.published_at else None

    @property
    def idx_repository(self) -> str:
        """Return repository for indexing."""
        return self.repository.path.lower()

    @property
    def idx_tag_name(self) -> str:
        """Return tag name for indexing."""
        return self.tag_name
