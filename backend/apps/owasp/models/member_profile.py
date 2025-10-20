"""OWASP app member profile model."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel
from apps.github.models.user import User


class MemberProfile(TimestampedModel):
    """OWASP Member Profile model.

    Stores OWASP-specific metadata for community members.
    """

    class Meta:
        db_table = "owasp_member_profiles"
        verbose_name_plural = "Member Profiles"

    github_user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="owasp_profile",
        help_text="Associated GitHub user",
    )
    owasp_slack_id = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="OWASP Slack ID",
        help_text="Member's Slack user ID in OWASP workspace",
    )
    first_contribution_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="First OWASP Contribution",
        help_text="Date of the member's first contribution to OWASP repositories",
    )

    def __str__(self) -> str:
        """Return human-readable representation."""
        return f"OWASP member profile for {self.github_user.login}"
