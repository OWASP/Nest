"""Nest Reminder model."""

from django.db import models


class Reminder(models.Model):
    """Model representing a reminder."""

    class Meta:
        db_table = "nest_reminders"
        verbose_name = "Nest Reminder"
        verbose_name_plural = "Nest Reminders"

    entity_channel = models.ForeignKey(
        "owasp.EntityChannel",
        verbose_name="Channel",
        on_delete=models.CASCADE,
        related_name="reminders",
    )
    event = models.ForeignKey(
        "owasp.Event",
        verbose_name="Event",
        on_delete=models.SET_NULL,
        related_name="reminders",
        null=True,
    )
    member = models.ForeignKey(
        "slack.Member",
        verbose_name="Slack Member",
        on_delete=models.SET_NULL,
        related_name="reminders",
        null=True,
    )
    message = models.TextField(verbose_name="Reminder Message")

    def __str__(self) -> str:
        """Reminder human readable representation."""
        return f"Reminder for {self.member} in channel: {self.entity_channel}: {self.message}"
