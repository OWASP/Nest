"""GitHub release model mixins for index-related functionality."""

from __future__ import annotations

from apps.common.utils import truncate

DESCRIPTION_MAX_LENGTH = 1000


class ReleaseIndexMixin:
    """Release index mixin."""

    @property
    def is_indexable(self) -> bool:
        """Determine if the release should be indexed.

        Returns:
            bool: True if the release is not a draft, False otherwise.

        """
        return not self.is_draft

    @property
    def idx_author(self) -> list[dict[str, str]]:
        """Return author for indexing.

        Returns:
            list[dict[str, str]]: A list containing author details, or empty list.

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
        """Return created at timestamp for indexing.

        Returns:
            float: The release creation timestamp.

        """
        return self.created_at.timestamp()

    @property
    def idx_description(self) -> str:
        """Return description for indexing.

        Returns:
            str: The truncated release description.

        """
        return truncate(self.description, limit=DESCRIPTION_MAX_LENGTH)

    @property
    def idx_is_pre_release(self) -> bool:
        """Return pre-release status for indexing.

        Returns:
            bool: True if the release is a pre-release, False otherwise.

        """
        return self.is_pre_release

    @property
    def idx_name(self) -> str:
        """Return name for indexing.

        Returns:
            str: The name of the release.

        """
        return self.name

    @property
    def idx_project(self) -> str:
        """Return project for indexing.

        Returns:
            str: The nest key of the associated project, or empty string.

        """
        return self.repository.project.nest_key if self.repository.project else ""

    @property
    def idx_published_at(self) -> float | None:
        """Return published at timestamp for indexing.

        Returns:
            float | None: The release publication timestamp, or None.

        """
        return self.published_at.timestamp() if self.published_at else None

    @property
    def idx_repository(self) -> str:
        """Return repository for indexing.

        Returns:
            str: The repository path in lowercase.

        """
        return self.repository.path.lower()

    @property
    def idx_tag_name(self) -> str:
        """Return tag name for indexing.

        Returns:
            str: The tag name of the release.

        """
        return self.tag_name
