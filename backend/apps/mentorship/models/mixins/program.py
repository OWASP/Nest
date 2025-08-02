"""Mentorship program mixins."""

from __future__ import annotations


class ProgramIndexMixin:
    """Program index mixin for mentorship programs."""

    @property
    def is_indexable(self) -> bool:
        """Only index published programs."""
        return self.status == self.__class__.ProgramStatus.PUBLISHED

    @property
    def idx_name(self) -> str:
        """Name for Algolia indexing."""
        return self.name

    @property
    def idx_key(self) -> str:
        """Unique key for Algolia indexing."""
        return self.key

    @property
    def idx_status(self) -> str:
        """Status for Algolia indexing."""
        return self.status

    @property
    def idx_description(self) -> str:
        """Description for Algolia indexing."""
        return self.description or ""

    @property
    def idx_experience_levels(self) -> list[str]:
        """List of experience levels for Algolia filtering."""
        return self.experience_levels or []

    @property
    def idx_admins(self) -> list[dict]:
        """List of program admins with their names and GitHub usernames."""
        return [
            {
                "name": getattr(admin, "name", "") or "",
                "login": getattr(admin, "github_username", "") or "",
            }
            for admin in self.admins.all()
        ]

    @property
    def idx_started_at(self) -> str | None:
        """Formatted start datetime."""
        return self.started_at.isoformat() if self.started_at else None

    @property
    def idx_ended_at(self) -> str | None:
        """Formatted end datetime for filtering/sorting."""
        return self.ended_at.isoformat() if self.ended_at else None

    @property
    def idx_modules(self) -> list[str]:
        """List of associated module names for indexing."""
        return list(self.modules.values_list("name", flat=True).distinct())
