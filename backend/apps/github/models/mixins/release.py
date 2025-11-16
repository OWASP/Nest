"""GitHub release model mixins for index-related functionality."""

from __future__ import annotations

from django.utils.text import Truncator


class ReleaseIndexMixin:
    """Release index mixin for GitHub projects."""

    @property
    def is_indexable(self) -> bool:
        """Determine if the release should be indexed.

        Purpose:
            Only releases that are not drafts are considered indexable
            to ensure that incomplete or unpublished releases are ignored.
        """
        return not self.is_draft

    @property
    def idx_author(self) -> list[dict[str, str]]:
        """Return release author information for indexing.

        Purpose:
            Provides top contributor details (avatar, login, name)
            to enhance indexing and search relevance.
        """
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
        """Return the release creation timestamp for indexing.

        Purpose:
            Supplies created_at timestamp for sorting or filtering
            releases in search indices.
        """
        return self.created_at.timestamp()

    @property
    def idx_description(self) -> str:
        """Return truncated release description for indexing.

        Purpose:
            Provides a concise description of the release (up to 1000 characters)
            for search indexing and display.
        """
        return Truncator(self.description).chars(1000, truncate="...")

    @property
    def idx_is_pre_release(self) -> bool:
        """Return pre-release status for indexing.

        Purpose:
            Indicates whether the release is a pre-release to filter
            or label releases accordingly in search indices.
        """
        return self.is_pre_release

    @property
    def idx_name(self) -> str:
        """Return release name for indexing.

        Purpose:
            Provides the release name for display and indexing purposes.
        """
        return self.name

    @property
    def idx_project(self) -> str:
        """Return associated project key for indexing.

        Purpose:
            Links the release to its parent project for
            better context in search results.
        """
        return self.repository.project.nest_key if self.repository.project else ""

    @property
    def idx_published_at(self) -> float | None:
        """Return release published timestamp for indexing.

        Purpose:
            Supplies published_at timestamp for chronological indexing
            and filtering.
        """
        return self.published_at.timestamp() if self.published_at else None

    @property
    def idx_repository(self) -> str:
        """Return repository path for indexing.

        Purpose:
            Provides repository identification for linking releases
            to their source repositories in the index.
        """
        return self.repository.path.lower()

    @property
    def idx_tag_name(self) -> str:
        """Return release tag name for indexing.

        Purpose:
            Supplies the release tag name to uniquely identify the release
            within the repository.
        """
        return self.tag_name
