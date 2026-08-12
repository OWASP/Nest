"""OWASP app activity event model."""

import logging

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.github.models.generic_issue_model import GenericIssueModel

logger = logging.getLogger(__name__)


class ActivityEvent(BulkSaveModel, TimestampedModel):
    """Represents a discrete GitHub activity event linked to a single source object.

    Uses a polymorphic GenericForeignKey to reference the source object.
    """

    class Meta:
        """Model options."""

        db_table = "github_activity_events"
        verbose_name_plural = "Activity Events"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "activity_type",
                    "content_type",
                    "object_id",
                    "occurred_at",
                ],
                name="unique_activity_event",
            ),
        ]

        indexes = [
            models.Index(fields=["activity_type"], name="activity_event_type_idx"),
            models.Index(fields=["github_user"], name="activity_event_github_user_idx"),
            models.Index(
                fields=["content_type", "object_id"],
                name="activity_event_source_idx",
            ),
            models.Index(fields=["occurred_at"], name="activity_event_occurred_at_idx"),
            models.Index(fields=["github_repository"], name="activity_event_github_repo_idx"),
        ]

    class ActivityType(models.TextChoices):
        """Activity type choices."""

        ISSUE_CLOSED = "issue_closed", "Issue Closed"
        ISSUE_OPENED = "issue_opened", "Issue Opened"
        PR_CLOSED = "pr_closed", "PR Closed"
        PR_MERGED = "pr_merged", "PR Merged"
        PR_OPENED = "pr_opened", "PR Opened"
        RELEASE_PUBLISHED = "release_published", "Release Published"

    activity_type = models.CharField(
        verbose_name="Activity Type",
        max_length=32,
        choices=ActivityType.choices,
    )
    github_user = models.ForeignKey(
        "github.User",
        verbose_name="GitHub User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="activity_events",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    occurred_at = models.DateTimeField(
        verbose_name="Occurred at",
        help_text="Timestamp when the activity event occurred on GitHub",
    )
    github_repository = models.ForeignKey(
        "github.Repository",
        verbose_name="GitHub Repository",
        on_delete=models.CASCADE,
        related_name="activity_events",
    )
    source_object = GenericForeignKey("content_type", "object_id")

    HANDLERS: dict[str, str] = {
        "Issue": "build_for_issue",
        "PullRequest": "build_for_pull_request",
        "Release": "build_for_release",
    }

    def __str__(self) -> str:
        """Return human-readable representation."""
        return f"{self.activity_type} by {self.github_user} in {self.github_repository}"

    @staticmethod
    def bulk_save(activity_events, fields=None) -> None:  # type: ignore[override]
        """Bulk save activity events."""
        BulkSaveModel.bulk_save(ActivityEvent, activity_events, fields=fields)

    @staticmethod
    def build_for_issue(issue) -> list[tuple]:
        """Return event tuples for an Issue."""
        events = [(ActivityEvent.ActivityType.ISSUE_OPENED, issue.created_at, issue.author)]
        if issue.state == GenericIssueModel.IssueState.CLOSED and issue.closed_at:
            events.append((ActivityEvent.ActivityType.ISSUE_CLOSED, issue.closed_at, issue.author))
        return events

    @staticmethod
    def build_for_pull_request(pr) -> list[tuple]:
        """Return event tuples for a PullRequest."""
        events = [(ActivityEvent.ActivityType.PR_OPENED, pr.created_at, pr.author)]
        if pr.merged_at:
            events.append((ActivityEvent.ActivityType.PR_MERGED, pr.merged_at, pr.author))
        elif pr.state == GenericIssueModel.IssueState.CLOSED and pr.closed_at:
            events.append((ActivityEvent.ActivityType.PR_CLOSED, pr.closed_at, pr.author))
        return events

    @staticmethod
    def build_for_release(release) -> list[tuple]:
        """Return event tuples for a Release."""
        if release.published_at is None:
            return []

        return [
            (ActivityEvent.ActivityType.RELEASE_PUBLISHED, release.published_at, release.author)
        ]

    @staticmethod
    def update_data(source) -> list["ActivityEvent"]:
        """Return unsaved ActivityEvent instances for a GitHub model object."""
        handler_name = ActivityEvent.HANDLERS.get(type(source).__name__)
        if handler_name is None:
            logger.error(
                "ActivityEvent.update_data received unsupported model type: %s",
                type(source).__name__,
            )
            message = f"Unsupported model type: {type(source)}"
            raise TypeError(message)

        handler = getattr(ActivityEvent, handler_name)
        events = handler(source)
        content_type = ContentType.objects.get_for_model(source)

        return [
            ActivityEvent(
                activity_type=activity_type,
                content_type=content_type,
                object_id=source.pk,
                occurred_at=occurred_at,
                github_user=github_user,
                github_repository=source.repository,
            )
            for activity_type, occurred_at, github_user in events
            if occurred_at is not None
        ]

    @staticmethod
    def bulk_save_for_sources(sources: list) -> None:
        """Bulk-insert ActivityEvent rows for source objects, skipping duplicates."""
        events = [event for source in sources for event in ActivityEvent.update_data(source)]
        if events:
            ActivityEvent.objects.bulk_create(events, ignore_conflicts=True)
