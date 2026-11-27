"""Mentor model for the Mentorship app."""

from __future__ import annotations

from apps.common.models import TimestampedModel
from apps.mentorship.models.common import (
    ExperienceLevel,
    LinkedUser,
    MatchingAttributes,
)


class Mentor(LinkedUser, ExperienceLevel, MatchingAttributes, TimestampedModel):
    """Mentor model."""

    class Meta:
        """Model options."""

        db_table = "mentorship_mentors"
        verbose_name_plural = "Mentors"

    def __str__(self) -> str:
        """Return a human-readable representation of the mentor.

        Returns:
            str: The GitHub username of the mentor.

        """
        return self.github_user.login
