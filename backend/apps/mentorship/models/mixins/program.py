"""Mentorship program mixins."""

from __future__ import annotations


class ProgramIndexMixin:
    """Program index mixin for mentorship programs."""

    @property
    def is_indexable(self) -> bool:
        """Determine if the program is indexable.

        Returns:
            bool: True if the program is published, False otherwise.
        """
        return self.status == self.__class__.ProgramStatus.PUBLISHED

    @property
    def idx_name(self) -> str:
        """Return the name for indexing.

        Returns:
            str: The name of the program.
        """
        return self.name

    @property
    def idx_key(self) -> str:
        """Return the unique key for indexing.

        Returns:
            str: The unique key of the program.
        """
        return self.key

    @property
    def idx_status(self) -> str:
        """Return the status for indexing.

        Returns:
            str: The status of the program.
        """
        return self.status

    @property
    def idx_description(self) -> str:
        """Return the description for indexing.

        Returns:
            str: The description of the program.
        """
        return self.description or ""

    @property
    def idx_experience_levels(self) -> list[str]:
        """Return the experience levels for indexing.

        Returns:
            list[str]: A list of experience levels required for the program.
        """
        return self.experience_levels or []

    @property
    def idx_started_at(self) -> str | None:
        """Return the formatted start date for indexing.

        Returns:
            str | None: The ISO formatted start date of the program, or None.
        """
        return self.started_at.isoformat() if self.started_at else None

    @property
    def idx_ended_at(self) -> str | None:
        """Return the formatted end date for indexing.

        Returns:
            str | None: The ISO formatted end date of the program, or None.
        """
        return self.ended_at.isoformat() if self.ended_at else None
