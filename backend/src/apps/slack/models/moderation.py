"""Store Slack moderation rules and sent-alert records.

ModerationRule configures which channel/emoji reaches which threshold.
ModerationAlert prevents sending duplicate moderator alerts for the same
message and report type.
"""

from typing import override

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimestampedModel
from apps.slack.models.conversation import Conversation


class ModerationRule(TimestampedModel):
    """Channel-specific emoji threshold and alert target."""

    class Meta:
        """Model options."""

        db_table = "slack_moderation_rules"
        unique_together = ("conversation", "emoji_name")

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    emoji_name = models.CharField(max_length=64)
    report_type = models.CharField(max_length=64)
    threshold = models.PositiveSmallIntegerField(default=3, validators=[MinValueValidator(1)])
    alert_channel_id = models.CharField(max_length=50)
    alert_user_ids = models.JSONField(blank=True, default=list)
    is_enabled = models.BooleanField(default=True)

    @override
    def __str__(self):
        return f"{self.conversation} :{self.emoji_name}"


class ModerationAlert(TimestampedModel):
    """Record that an alert was already sent for a reported message."""

    class Meta:
        """Model options."""

        db_table = "slack_moderation_alerts"
        unique_together = ("conversation", "message_ts", "report_type")

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    message_ts = models.CharField(max_length=32)
    report_type = models.CharField(max_length=64)
    reaction_count = models.PositiveSmallIntegerField(default=0)
    alert_message_ts = models.CharField(max_length=32, blank=True, default="")
