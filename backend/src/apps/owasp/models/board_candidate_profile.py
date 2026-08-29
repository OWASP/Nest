"""OWASP app Board Candidate Profile model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.owasp.models.entity_member import EntityMember


class BoardCandidateProfile(TimestampedModel):
    """Model representing a Board Candidate Profile's markdown content."""

    class Meta:
        """Model options."""

        db_table = "owasp_board_candidate_profiles"
        verbose_name_plural = "Board Candidate Profiles"

    candidate = models.OneToOneField(
        EntityMember,
        help_text="The candidate this profile belongs to.",
        limit_choices_to={"role": EntityMember.Role.CANDIDATE},
        on_delete=models.CASCADE,
        related_name="board_profile",
    )
    raw_markdown = models.TextField(
        blank=True,
        default="",
        help_text="The raw markdown content of the candidate's profile.",
    )

    def __str__(self) -> str:
        """Return a string representation of the Board Candidate Profile."""
        return f"Profile for {self.candidate.member_name}"
