"""Store emitted Slack reaction alerts."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.slack.models.conversation import Conversation


class ReactionAlert(TimestampedModel):
    """Record that an alert was already sent for a reported message."""

    class Meta:
        """Model options."""

        db_table = "slack_reaction_alerts"
        unique_together = ("conversation", "message_ts", "report_type")

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    message_ts = models.CharField(
        max_length=32,
        help_text="Slack timestamp of the message that triggered the alert.",
    )
    report_type = models.CharField(
        max_length=64,
        help_text="Report category for the emitted reaction alert.",
    )
    reaction_count = models.PositiveSmallIntegerField(default=0)
    alert_message_ts = models.CharField(
        max_length=32,
        blank=True,
        default="",
        help_text="Slack timestamp of the posted reaction alert message.",
    )
