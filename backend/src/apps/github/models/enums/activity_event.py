"""Enums for GitHub activity events."""

from django.db import models


class ActivityType(models.TextChoices):
    """Activity type choices."""

    COMMIT_PUSHED = "commit_pushed", "Commit Pushed"
    ISSUE_CLOSED = "issue_closed", "Issue Closed"
    ISSUE_OPENED = "issue_opened", "Issue Opened"
    PR_CLOSED = "pr_closed", "PR Closed"
    PR_MERGED = "pr_merged", "PR Merged"
    PR_OPENED = "pr_opened", "PR Opened"
    RELEASE_PUBLISHED = "release_published", "Release Published"
