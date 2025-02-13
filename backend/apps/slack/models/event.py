"""Slack app event model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.slack.commands.owasp import COMMAND as OWASP_COMMAND


class Event(TimestampedModel):
    """Event model."""

    class Meta:
        db_table = "slack_events"
        verbose_name_plural = "Events"

    channel_id = models.CharField(verbose_name="Channel ID", max_length=15, default="")
    channel_name = models.CharField(verbose_name="Channel name", max_length=100, default="")
    text = models.CharField(verbose_name="Text", max_length=1000, default="")
    trigger = models.CharField(verbose_name="Trigger", max_length=100, default="")
    user_id = models.CharField(verbose_name="User ID", max_length=15)
    user_name = models.CharField(verbose_name="User name", max_length=100, default="")

    def __str__(self):
        """Event human readable representation."""
        return f"Event from {self.user_name or self.user_id} triggered by {self.trigger}"

    def from_slack(self, context, payload):
        """Create instance based on Slack data."""
        self.channel_id = context.get("channel_id", "")
        self.channel_name = payload.get("channel_name", "")

        command = payload.get("command", "")
        text = payload.get("text", "")
        if command and command == OWASP_COMMAND:
            command, *args = text.strip().split()
            text = " ".join(args)
        self.command = command.lstrip("/")
        self.text = text

        # In this order.
        self.trigger = self.command or payload.get("action_id", "") or payload.get("type", "")
        self.user_id = context["user_id"]
        self.user_name = payload.get("user_name", "")

    @staticmethod
    def create(context, payload, save=True):
        """Create event."""
        event = Event()
        event.from_slack(context, payload)
        if save:
            event.save()

        return event
