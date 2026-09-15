"""OWASP app board meeting model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.owasp.models.board_of_directors import BoardOfDirectors
from apps.owasp.models.entity_member import EntityMember


class BoardMeeting(TimestampedModel):
    """Board meeting model."""

    class Type(models.TextChoices):
        """Board meeting type choices."""

        PRIVATE = "private", "Private"
        PUBLIC = "public", "Public"
        SPECIAL = "special", "Special"
        SUMMIT = "summit", "Summit"

    class Meta:
        """Model options."""

        db_table = "owasp_board_meetings"
        verbose_name_plural = "Board Meetings"

    attachments = models.JSONField(default=list, blank=True)
    call_in_url = models.URLField(blank=True, default="")
    date = models.DateTimeField()
    guests = models.JSONField(default=list, blank=True)
    location = models.CharField(max_length=255, blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    quorum_present = models.BooleanField(blank=True, null=True)
    recording_url = models.URLField(blank=True, default="")
    source_checksum = models.CharField(max_length=64, blank=True, default="")
    source_path = models.CharField(max_length=500, unique=True)
    title = models.CharField(max_length=255, blank=True, default="")
    type = models.CharField(max_length=7, choices=Type.choices, default=Type.PUBLIC)

    absentees = models.ManyToManyField(EntityMember, blank=True, related_name="+")
    attendees = models.ManyToManyField(EntityMember, blank=True, related_name="+")

    board = models.ForeignKey(
        BoardOfDirectors,
        on_delete=models.CASCADE,
        related_name="meetings",
    )

    def __str__(self) -> str:
        """Return the board meeting human-readable representation."""
        label = self.title or self.date.isoformat()
        return f"Board Meeting: {label}"
