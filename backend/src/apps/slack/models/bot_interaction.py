"""Slack app bot interaction model."""

from django.db import models

from apps.common.models import TimestampedModel


class BotInteraction(TimestampedModel):
    """Tracks AI-generated replies and their user feedback."""

    class Meta:
        """Model options."""

        db_table = "slack_bot_interactions"
        verbose_name_plural = "Bot Interactions"

    channel_id = models.CharField(verbose_name="Channel ID", max_length=64)
    user_id = models.CharField(verbose_name="User ID", max_length=64)
    user_message = models.TextField(verbose_name="User message")
    bot_response = models.TextField(verbose_name="Bot response")
    intent_category = models.CharField(
        verbose_name="Intent category", max_length=64, blank=True, default=""
    )
    confidence_score = models.FloatField(
        verbose_name="Confidence score", null=True, blank=True
    )
    thumbs_up = models.BooleanField(
        verbose_name="Thumbs up",
        null=True,
        blank=True,
        help_text="True = 👍, False = 👎, None = no reaction yet.",
    )
    tokens_used = models.PositiveIntegerField(verbose_name="Tokens used", default=0)
    slack_reply_ts = models.CharField(
        verbose_name="Slack reply timestamp",
        max_length=32,
        blank=True,
        default="",
        db_index=True,
        help_text="Slack message ts of the bot reply. Used to match reaction_added events.",
    )

    def __str__(self):
        """Return human readable representation."""
        feedback = {True: "👍", False: "👎", None: "—"}[self.thumbs_up]
        return f"[{self.channel_id}] {self.user_message[:50]!r} → {feedback}"
