"""OWASP app member profile model."""

from __future__ import annotations

from django.core.validators import RegexValidator
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
    is_owasp_board_member = models.BooleanField(
        default=False,
        verbose_name="Is OWASP Board Member",
        help_text="Whether the member is currently serving on the OWASP Board of Directors",
    )
    is_former_owasp_staff = models.BooleanField(
        default=False,
        verbose_name="Is Former OWASP Staff",
        help_text="Whether the member is a former OWASP staff member",
    )
    is_gsoc_mentor = models.BooleanField(
        default=False,
        verbose_name="Is GSoC Mentor",
        help_text="Whether the member is a Google Summer of Code mentor",
    )
    linkedin_page_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z0-9\-]{3,100}$",
                message=(
                    "LinkedIn ID must be 3-100 characters and contain only "
                    "letters, numbers, and hyphens"
                ),
                code="invalid_linkedin_id",
            ),
        ],
        verbose_name="LinkedIn Page ID",
        help_text="LinkedIn username or custom URL ID (e.g., 'john-doe-123')",
    )
    has_public_member_page = models.BooleanField(
        default=True,
        verbose_name="Has Public Member Page",
        help_text="Whether the member's profile is publicly visible on the OWASP website",
    )
    is_owasp_staff = models.BooleanField(
        default=False,
        verbose_name="Is OWASP Staff",
        help_text="Indicates if the user is OWASP Foundation staff.",
    )
    contributions_count = models.PositiveIntegerField(
        verbose_name="Contributions count", default=0
    )

    def __str__(self) -> str:
        """Return human-readable representation."""
        return f"OWASP member profile for {self.github_user.login}"
