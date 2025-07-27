from __future__ import annotations
from datetime import datetime


class ProgramIndexMixin:
    """Program index mixin for mentorship programs."""

    @property
    def is_indexable(self) -> bool:
        """Only index published programs."""
        return self.status == self.__class__.ProgramStatus.PUBLISHED

    @property
    def idx_name(self) -> str:
        return self.name

    @property
    def idx_key(self) -> str:
        return self.key

    @property
    def idx_status(self) -> str:
        return self.status

    @property
    def idx_description(self) -> str:
        return self.description or ""

    @property
    def idx_experience_levels(self) -> list[str]:
        return self.experience_levels or []

    @property
    def idx_admins(self) -> list[dict]:
        return [
            {
                "name": getattr(admin, "name", "") or "",
                "login": getattr(admin, "github_username", "") or "",
            }
            for admin in self.admins.all()
        ]

    @property
    def idx_started_at(self) -> str | None:
        """ISO 8601 start datetime for Algolia filtering/sorting."""
        if self.started_at:
            return self.started_at.isoformat()
        return None

    @property
    def idx_ended_at(self) -> str | None:
        """ISO 8601 end datetime for Algolia filtering/sorting."""
        if self.ended_at:
            return self.ended_at.isoformat()
        return None
