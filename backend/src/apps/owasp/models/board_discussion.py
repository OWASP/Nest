"""OWASP app board discussion model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.owasp.models.entity_member import EntityMember


class BoardDiscussion(TimestampedModel):
    """Board discussion model."""

    class Meta:
        """Model options."""

        db_table = "owasp_board_discussions"
        verbose_name_plural = "Board Discussions"

    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    topic = models.CharField(max_length=500)

    participants = models.ManyToManyField(
        EntityMember,
        blank=True,
        related_name="+",
    )

    def __str__(self) -> str:
        """Return the board discussion human-readable representation."""
        return f"Discussion: {self.topic}"
