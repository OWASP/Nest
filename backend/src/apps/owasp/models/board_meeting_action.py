"""OWASP app board meeting action model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.owasp.models.board_discussion import BoardDiscussion
from apps.owasp.models.board_meeting import BoardMeeting
from apps.owasp.models.board_motion import BoardMotion
from apps.owasp.models.board_outcome import BoardOutcome


class BoardMeetingAction(TimestampedModel):
    """Board meeting action model."""

    class Meta:
        """Model options."""

        db_table = "owasp_board_meeting_actions"
        verbose_name_plural = "Board Meeting Actions"
        constraints = [
            models.UniqueConstraint(
                fields=["meeting", "order"],
                name="board_meeting_action_unique_meeting_order",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        discussion__isnull=False,
                        motion__isnull=True,
                        outcome__isnull=True,
                    )
                    | models.Q(
                        discussion__isnull=True,
                        motion__isnull=False,
                        outcome__isnull=True,
                    )
                    | models.Q(
                        discussion__isnull=True,
                        motion__isnull=True,
                        outcome__isnull=False,
                    )
                ),
                name="board_meeting_action_exactly_one_target",
            ),
        ]

    order = models.PositiveIntegerField()

    discussion = models.ForeignKey(
        BoardDiscussion,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    meeting = models.ForeignKey(
        BoardMeeting,
        on_delete=models.CASCADE,
        related_name="actions",
    )
    motion = models.ForeignKey(
        BoardMotion,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    outcome = models.ForeignKey(
        BoardOutcome,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="+",
    )

    def __str__(self) -> str:
        """Return the board meeting action human-readable representation."""
        return f"Meeting Action #{self.order} in meeting {self.meeting_id}"
