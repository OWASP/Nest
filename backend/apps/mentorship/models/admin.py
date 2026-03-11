"""Admin model for the Mentorship app."""

from apps.common.models import TimestampedModel
from apps.mentorship.models.common import (
    ExperienceLevel,
    LinkedUser,
    MatchingAttributes,
)


class Admin(LinkedUser, ExperienceLevel, MatchingAttributes, TimestampedModel):
    """Admin model."""

    class Meta:
        """Model options."""

        db_table = "mentorship_admins"
        verbose_name_plural = "Admins"

    def __str__(self) -> str:
        """Return a human-readable representation of the admin.

        Returns:
            str: The GitHub username of the admin.

        """
        return self.github_user.login
