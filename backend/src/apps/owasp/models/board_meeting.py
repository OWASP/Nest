"""OWASP app board meeting model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.owasp.models.board_discussion import BoardDiscussion
from apps.owasp.models.board_motion import BoardMotion
from apps.owasp.models.board_of_directors import BoardOfDirectors
from apps.owasp.models.board_outcome import BoardOutcome
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

    def clear_agenda(self) -> None:
        """Delete this meeting's action links and their exclusive target rows."""
        actions = list(self.actions.all())
        discussion_ids = [action.discussion_id for action in actions if action.discussion_id]
        motion_ids = [action.motion_id for action in actions if action.motion_id]
        outcome_ids = [action.outcome_id for action in actions if action.outcome_id]

        # Remove action links first so target deletes cannot cascade into other meetings.
        self.actions.all().delete()
        if discussion_ids:
            BoardDiscussion.objects.filter(id__in=discussion_ids).delete()
        if motion_ids:
            BoardMotion.objects.filter(id__in=motion_ids).delete()
        if outcome_ids:
            BoardOutcome.objects.filter(id__in=outcome_ids).delete()

    def delete(self, *args, **kwargs):
        """Delete the meeting and orphaned discussion/motion/outcome rows."""
        self.clear_agenda()
        return super().delete(*args, **kwargs)
