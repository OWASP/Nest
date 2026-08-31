"""OWASP app board motion model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.owasp.models.entity_member import EntityMember


class BoardMotion(TimestampedModel):
    """Board motion model."""

    class Meta:
        """Model options."""

        db_table = "owasp_board_motions"
        verbose_name_plural = "Board Motions"

    background = models.TextField(blank=True, default="")
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    references = models.JSONField(default=list, blank=True)
    title = models.CharField(max_length=500)

    amends_motion = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    second = models.ForeignKey(
        EntityMember,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    sponsor = models.ForeignKey(
        EntityMember,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    def __str__(self) -> str:
        """Return the board motion human-readable representation."""
        return f"Motion: {self.title}"
