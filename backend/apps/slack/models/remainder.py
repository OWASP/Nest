"""Slack remainder model."""

from django.db import models


class Remainder(models.Model):
    """Model representing a slack channel remainder."""

    class Meta:
        db_table = "slack_remainders"
        verbose_name = "Slack Remainder"
        verbose_name_plural = "Slack Remainders"

    member = models.ForeignKey(
        "slack.Member",
        verbose_name="Slack Member",
        on_delete=models.SET_NULL,
        null=True,
    )
    channel = models.ForeignKey(
        "slack.EntityChannel",
        verbose_name="Slack Channel",
        on_delete=models.CASCADE,
    )
    message = models.TextField(verbose_name="Reminder Message")
    remind_at = models.DateTimeField(verbose_name="Reminder Time")
    periodic = models.BooleanField(default=False, verbose_name="Is Periodic")

    def __str__(self) -> str:
        """Remainder human readable representation."""
        return f"Reminder for {self.member} in {self.channel}: {self.message} at {self.remind_at}"
