"""Nest Reminder model."""

from django.db import models


class Reminder(models.Model):
    """Model representing a reminder."""

    class Meta:
        db_table = "nest_reminders"
        verbose_name = "Nest Reminder"
        verbose_name_plural = "Nest Reminders"

    member = models.ForeignKey(
        "slack.Member",
        verbose_name="Slack Member",
        on_delete=models.SET_NULL,
        related_name="reminders",
        null=True,
    )
    channel_id = models.CharField(verbose_name="Channel ID", max_length=15, default="")
    message = models.TextField(verbose_name="Reminder Message")

    def __str__(self) -> str:
        """Reminder human readable representation."""
        return f"Reminder for {self.member} in channel: {self.channel_id}: {self.message}"
