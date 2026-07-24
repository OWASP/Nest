"""Store channel-specific Slack reaction rules."""

from typing import override

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimestampedModel
from apps.slack.models.conversation import Conversation


class ReactionRule(TimestampedModel):
    """Channel-specific emoji threshold and alert target."""

    class Meta:
        """Model options."""

        db_table = "slack_reaction_rules"
        unique_together = ("conversation", "emoji_name")

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    emoji_name = models.CharField(
        max_length=64,
        help_text="Slack emoji name that triggers this reaction rule.",
    )
    report_type = models.CharField(
        max_length=64,
        help_text="Report category recorded when this reaction rule triggers.",
    )
    threshold = models.PositiveSmallIntegerField(default=3, validators=[MinValueValidator(1)])
    alert_channel_id = models.CharField(
        max_length=50,
        help_text="Slack channel ID where reaction alerts are posted.",
    )
    alert_user_ids = models.JSONField(blank=True, default=list)
    is_enabled = models.BooleanField(default=True)

    @override
    def __str__(self):
        return f"{self.conversation} :{self.emoji_name}"
