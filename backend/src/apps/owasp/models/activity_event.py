"""OWASP app activity event model."""

from datetime import timedelta
import logging

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.github.models.user import User

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

    TIME_RANGES: dict[str, timedelta] = {
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "90d": timedelta(days=90),
        "180d": timedelta(days=180),
        "1y": timedelta(days=365),
        "2y": timedelta(days=730),
    }

    def __str__(self) -> str:
        """Return human-readable representation."""
        return f"{self.activity_type} by {self.github_user} in {self.github_repository}"

    @property
    def source_number(self) -> int | None:
        """Return issue or PR number from the source object, if applicable."""
        return getattr(self.source_object, "number", None)

    @property
    def source_title(self) -> str:
        """Return title or name from the source object."""
        if not self.source_object:
            return ""
        return getattr(self.source_object, "title", getattr(self.source_object, "name", ""))

    @property
    def source_url(self) -> str:
        """Return URL from the source object."""
        return getattr(self.source_object, "url", "") if self.source_object else ""

    @classmethod
    def exclude_bots(cls, queryset):
        """Exclude bot accounts from the given queryset."""
        return queryset.exclude(
            Q(github_user__is_bot=True)
            | Q(github_user__login__in=User.get_non_indexable_logins())
        )

    @classmethod
    def filter_time_range(cls, queryset, time_range: str):
        """Filter queryset by time range."""
        if not time_range:
            return queryset

        if delta := cls.TIME_RANGES.get(time_range):
            return queryset.filter(occurred_at__gte=timezone.now() - delta)

        return queryset.none()

    @staticmethod
    def bulk_save(activity_events, fields=None) -> None:  # type: ignore[override]
        """Bulk save activity events."""
        BulkSaveModel.bulk_save(ActivityEvent, activity_events, fields=fields)

    @staticmethod
    def build_for_issue(issue) -> list[tuple]:
        """Return event tuples for an Issue."""
        events = [(ActivityEvent.ActivityType.ISSUE_OPENED, issue.created_at, issue.author)]
        if issue.state == "closed" and issue.closed_at:
            events.append((ActivityEvent.ActivityType.ISSUE_CLOSED, issue.closed_at, issue.author))
        return events

    @staticmethod
    def build_for_pull_request(pr) -> list[tuple]:
        """Return event tuples for a PullRequest."""
        events = [(ActivityEvent.ActivityType.PR_OPENED, pr.created_at, pr.author)]
        if pr.merged_at:
            events.append((ActivityEvent.ActivityType.PR_MERGED, pr.merged_at, pr.author))
        elif pr.state == "closed" and pr.closed_at:
            events.append((ActivityEvent.ActivityType.PR_CLOSED, pr.closed_at, pr.author))
        return events

    @staticmethod
    def build_for_release(release) -> list[tuple]:
        """Return event tuples for a Release."""
        occurred_at = release.published_at or release.created_at
        return [(ActivityEvent.ActivityType.RELEASE_PUBLISHED, occurred_at, release.author)]

    @staticmethod
    def update_data(obj) -> None:
        """Create ActivityEvent row(s) for a saved GitHub model instance if they do not exist."""
        handler_name = ActivityEvent.HANDLERS.get(type(obj).__name__)
        if handler_name is None:
            logger.error(
                "ActivityEvent.update_data received unsupported model type: %s",
                type(obj).__name__,
            )
            message = f"Unsupported model type: {type(obj)}"
            raise TypeError(message)

        handler = getattr(ActivityEvent, handler_name)
        events = handler(obj)
        content_type = ContentType.objects.get_for_model(obj)

        for activity_type, occurred_at, github_user in events:
            if occurred_at is None:
                continue

            ActivityEvent.objects.get_or_create(
                activity_type=activity_type,
                content_type=content_type,
                object_id=obj.pk,
                occurred_at=occurred_at,
                defaults={
                    "github_user": github_user,
                    "github_repository": obj.repository,
                },
            )
