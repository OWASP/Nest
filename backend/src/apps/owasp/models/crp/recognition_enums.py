"""Enums for OWASP contributor recognition program."""

from django.db import models


class EventTypeChoices(models.TextChoices):
    """Enum for contribution event types."""

    PR_MERGED = "pr_merged", "Pull Request Merged"
    PR_OPENED = "pr_opened", "Pull Request Opened"
    ISSUE_OPENED = "issue_opened", "Issue Opened"


class TierChoices(models.TextChoices):
    """Enum for contributor tiers."""

    LEVEL_1 = "level_1", "Level 1"
    LEVEL_2 = "level_2", "Level 2"
    LEVEL_3 = "level_3", "Level 3"
    LEVEL_4 = "level_4", "Level 4"
