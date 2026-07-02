"""Slack app event model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.slack.commands.owasp import Owasp

OWASP_COMMAND = Owasp().command_name


class Event(TimestampedModel):
    """Event model."""

    class Meta:
        """Model options."""

        db_table = "slack_events"
        verbose_name_plural = "Events"

    channel_id = models.CharField(verbose_name="Channel ID", max_length=15, default="")
    channel_name = models.CharField(verbose_name="Channel name", max_length=100, default="")
    text = models.CharField(verbose_name="Text", max_length=1000, default="")
    trigger = models.CharField(verbose_name="Trigger", max_length=100, default="")
    user_id = models.CharField(verbose_name="User ID", max_length=15)
    user_name = models.CharField(verbose_name="User name", max_length=100, default="")

    def __str__(self) -> str:
        """Event human readable representation.

        Returns
            str: A string representation of the event.

        """
        return f"Event from {self.user_name or self.user_id} triggered by {self.trigger}"

    def from_slack(self, context, payload) -> None:
        """Create instance based on Slack data.

        Args:
            context (dict): Context data from Slack, including user and channel information.
            payload (dict): Payload data from Slack, including command and text information.

        """
        self.channel_id = context.get("channel_id", "")
        self.channel_name = payload.get("channel_name", "")

        command = payload.get("command", "")
        text = payload.get("text", "")
        if command and command == OWASP_COMMAND:
            try:
                command, *args = text.strip().split()
                text = " ".join(args)
            except ValueError:
                pass
        self.command = command.lstrip("/")
        self.text = text

        # In this order.
        self.trigger = self.command or payload.get("action_id", "") or payload.get("type", "")
        self.user_id = context["user_id"]
        self.user_name = payload.get("user_name", "")

    @staticmethod
    def create(context: dict, payload: dict, *, save: bool = True) -> "Event":
        """Create event.

        Args:
            context (dict): Context data from Slack, including user and channel information.
            payload (dict): Payload data from Slack, including command and text information.
            save (bool, optional): Whether to save the event to the database.

        Returns:
            Event: The created Event instance.

        """
        event = Event()
        event.from_slack(context, payload)
        if save:
            event.save()

        return event
