"""Store channel-specific Slack reaction rules."""

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimestampedModel
from apps.slack.models.conversation import Conversation


class ReactionRule(TimestampedModel):
    """Channel-specific emoji threshold and alert target."""

    class ReportType(models.TextChoices):
        """Reaction report category choices."""

        SPAM = "spam", "Spam"

    class Meta:
        """Model options."""

        db_table = "slack_reaction_rules"
        unique_together = ("conversation", "emoji_name")

    alert_channel_id = models.CharField(
        max_length=50,
        help_text="Slack channel ID where reaction alerts are posted.",
    )
    alert_user_ids = models.JSONField(blank=True, default=list)
    emoji_name = models.CharField(
        max_length=64,
        help_text=(
            "Slack emoji name that triggers this reaction rule, without leading or "
            "trailing colons (spam, not :spam:)."
        ),
    )
    is_active = models.BooleanField(default=True)
    report_type = models.CharField(
        max_length=64,
        choices=ReportType.choices,
        default=ReportType.SPAM,
        help_text="Report category recorded when this reaction rule triggers.",
    )
    threshold = models.PositiveSmallIntegerField(default=3, validators=[MinValueValidator(1)])

    # FKs.
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)

    def __str__(self):
        """Human readable representation."""
        return f"{self.conversation} :{self.emoji_name}"

    @staticmethod
    def for_reaction(channel_id: str, emoji_name: str) -> "ReactionRule | None":
        """Get the active reaction rule for a channel and emoji, if configured."""
        return (
            ReactionRule.objects.select_related("conversation")
            .filter(
                conversation__slack_channel_id=channel_id,
                emoji_name=emoji_name,
                is_active=True,
            )
            .first()
        )
