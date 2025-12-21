"""GitHub release model mixins for index-related functionality."""

from __future__ import annotations

from apps.common.utils import truncate

DESCRIPTION_MAX_LENGTH = 1000


class ReleaseIndexMixin:
    """Release index mixin."""

    @property
    def is_indexable(self) -> bool:
        """Determine if the release is indexable.

        Returns:
            bool: True if the release is not a draft, False otherwise.
        """
        return not self.is_draft

    @property
    def idx_author(self) -> list[dict[str, str]]:
        """Return the author details for indexing.

        Returns:
            list[dict[str, str]]: A list containing a dictionary with author's avatar URL, login, and name.
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
        """Return the created at timestamp for indexing.

        Returns:
            float: The creation timestamp of the release.
        """
        return self.created_at.timestamp()

    @property
    def idx_description(self) -> str:
        """Return the truncated description for indexing.

        Returns:
            str: The truncated description of the release.
        """
        return truncate(self.description, limit=DESCRIPTION_MAX_LENGTH)

    @property
    def idx_is_pre_release(self) -> bool:
        """Return the pre-release status for indexing.

        Returns:
            bool: True if the release is a pre-release, False otherwise.
        """
        return self.is_pre_release

    @property
    def idx_name(self) -> str:
        """Return the name for indexing.

        Returns:
            str: The name of the release.
        """
        return self.name

    @property
    def idx_project(self) -> str:
        """Return the project nest key for indexing.

        Returns:
            str: The nest key of the associated project, or an empty string.
        """
        return self.repository.project.nest_key if self.repository.project else ""

    @property
    def idx_published_at(self) -> float | None:
        """Return the published at timestamp for indexing.

        Returns:
            float | None: The publication timestamp, or None if not available.
        """
        return self.published_at.timestamp() if self.published_at else None

    @property
    def idx_repository(self) -> str:
        """Return the lowercase repository path for indexing.

        Returns:
            str: The lowercase path of the repository.
        """
        return self.repository.path.lower()

    @property
    def idx_tag_name(self) -> str:
        """Return the tag name for indexing.

        Returns:
            str: The tag name of the release.
        """
        return self.tag_name
