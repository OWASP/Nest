"""Slack reminder model."""

from django.db import models


class Reminder(models.Model):
    """Model representing a slack channel reminder."""

    class Meta:
        db_table = "slack_reminders"
        verbose_name = "Slack Reminder"
        verbose_name_plural = "Slack Reminders"

    member = models.ForeignKey(
        "slack.Member",
        verbose_name="Slack Member",
        on_delete=models.SET_NULL,
        related_name="reminders",
        null=True,
    )
    channel_id = models.CharField(verbose_name="Channel ID", max_length=15, default="")
    message = models.TextField(verbose_name="Reminder Message")
    remind_at = models.DateTimeField(verbose_name="Reminder Time")
    periodic = models.BooleanField(default=False, verbose_name="Is Periodic")

    def __str__(self) -> str:
        """Reminder human readable representation."""
        return (
            f"Reminder for {self.member} in channel: "
            f"{self.channel_id}: {self.message} at {self.remind_at}"
        )
