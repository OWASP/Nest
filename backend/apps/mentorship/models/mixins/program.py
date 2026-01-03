"""Mentorship program mixins."""

from __future__ import annotations


class ProgramIndexMixin:
    """Program index mixin for mentorship programs."""

    @property
    def is_indexable(self) -> bool:
        """Determine if the program should be indexed.

        Returns:
            bool: True if the program is published, False otherwise.

        """
        return self.status == self.__class__.ProgramStatus.PUBLISHED

    @property
    def idx_name(self) -> str:
        """Return name for Algolia indexing.

        Returns:
            str: The program name.

        """
        return self.name

    @property
    def idx_key(self) -> str:
        """Return unique key for Algolia indexing.

        Returns:
            str: The program key.

        """
        return self.key

    @property
    def idx_status(self) -> str:
        """Return status for Algolia indexing.

        Returns:
            str: The program status.

        """
        return self.status

    @property
    def idx_description(self) -> str:
        """Return description for Algolia indexing.

        Returns:
            str: The program description.

        """
        return self.description or ""

    @property
    def idx_experience_levels(self) -> list[str]:
        """Return experience levels for Algolia filtering.

        Returns:
            list[str]: A list of experience levels.

        """
        return self.experience_levels or []

    @property
    def idx_started_at(self) -> str | None:
        """Return formatted start datetime.

        Returns:
            str | None: The start datetime in ISO format, or None.

        """
        return self.started_at.isoformat() if self.started_at else None

    @property
    def idx_ended_at(self) -> str | None:
        """Return formatted end datetime for filtering/sorting.

        Returns:
            str | None: The end datetime in ISO format, or None.

        """
        return self.ended_at.isoformat() if self.ended_at else None
