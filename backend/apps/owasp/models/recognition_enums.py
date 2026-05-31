"""Enums for OWASP contributor recognition program."""

from django.db import models


class EventTypeChoices(models.TextChoices):
    """Enum for contribution event types."""

    PR_MERGED = "pr_merged", "Pull Request Merged"
    PR_OPENED = "pr_opened", "Pull Request Opened"
    ISSUE_OPENED = "issue_opened", "Issue Opened"


class TierChoices(models.TextChoices):
    """Enum for contributor tiers."""

    BRONZE = "bronze", "Bronze"
    SILVER = "silver", "Silver"
    GOLD = "gold", "Gold"
    PLATINUM = "platinum", "Platinum"
