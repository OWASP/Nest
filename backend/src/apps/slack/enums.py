"""Shared Slack enumerations."""

from django.db import models


class ReportSource(models.TextChoices):
    """How a content report was created."""

    COMMAND = "command", "Command"
    EMOJI = "emoji", "Emoji"
    SHORTCUT = "shortcut", "Shortcut"


class ReportType(models.TextChoices):
    """Content report category choices (emoji rules and content reports)."""

    HARASSMENT = "harassment", "Harassment"
    OFF_TOPIC = "off_topic", "Off-topic"
    OTHER = "other", "Other"
    SPAM = "spam", "Spam"
