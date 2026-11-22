"""OWASP app activity event model."""

import logging
from datetime import timedelta

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Prefetch, Q
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
            models.Index(
                fields=["content_type", "object_id"],
                name="activity_event_source_idx",
            ),
            models.Index(fields=["occurred_at"], name="activity_event_occurred_at_idx"),
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

    MAX_LIMIT: int = 1000

    TIME_RANGES: dict[str, timedelta] = {
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "90d": timedelta(days=90),
        "180d": timedelta(days=180),
        "1y": timedelta(days=365),
        "2y": timedelta(days=730),
    }

    VALID_ORDER_VALUES: frozenset = frozenset({"asc", "desc"})

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
    def base_queryset(cls):
        """Return the standard queryset with select_related and prefetch_related applied."""
        from apps.github.models.release import Release  # noqa: PLC0415

        return cls.objects.select_related(
            "github_repository",
            "github_user",
        ).prefetch_related(
            Prefetch("source_object", queryset=Release.objects.select_related("repository")),
        )

    @classmethod
    def exclude_bots(cls, queryset):
        """Exclude bot accounts from the given queryset."""
        return queryset.exclude(
            Q(github_user__is_bot=True) | Q(github_user__login__in=User.get_non_indexable_logins())
        )

    @classmethod
    def filter_queryset(
        cls,
        queryset,
        *,
        activity_type: str | None = None,
        chapter_key: str | None = None,
        github_user: str | None = None,
        include_bots: bool = False,
        project_key: str | None = None,
        time_range: str | None = None,
    ):
        """Apply validated filter parameters to the queryset and return it."""
        from apps.github.models.issue import Issue  # noqa: PLC0415
        from apps.github.models.pull_request import PullRequest  # noqa: PLC0415
        from apps.github.models.release import Release  # noqa: PLC0415
        from apps.owasp.models.chapter import Chapter  # noqa: PLC0415
        from apps.owasp.models.project import Project  # noqa: PLC0415

        if not include_bots:
            queryset = cls.exclude_bots(queryset)

        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)

        if github_user:
            issue_ct = ContentType.objects.get_for_model(Issue)
            pr_ct = ContentType.objects.get_for_model(PullRequest)
            release_ct = ContentType.objects.get_for_model(Release)

            issue_ids = Issue.objects.filter(title__icontains=github_user).values_list(
                "pk", flat=True
            )
            pr_ids = PullRequest.objects.filter(title__icontains=github_user).values_list(
                "pk", flat=True
            )
            release_ids = Release.objects.filter(
                Q(name__icontains=github_user) | Q(tag_name__icontains=github_user)
            ).values_list("pk", flat=True)

            queryset = queryset.filter(
                Q(github_user__login__icontains=github_user)
                | Q(github_user__name__icontains=github_user)
                | Q(github_repository__name__icontains=github_user)
                | Q(github_repository__key__icontains=github_user)
                | Q(content_type=issue_ct, object_id__in=issue_ids)
                | Q(content_type=pr_ct, object_id__in=pr_ids)
                | Q(content_type=release_ct, object_id__in=release_ids)
            )

        if project_key:
            project_repo_ids = Project.objects.filter(
                Q(name__iexact=project_key) | Q(key__iexact=project_key)
            ).values_list("repositories", flat=True)
            queryset = queryset.filter(
                Q(github_repository__in=project_repo_ids)
                | Q(github_repository__name__iexact=project_key)
                | Q(github_repository__key__iexact=project_key)
            )

        if chapter_key:
            chapter_repo_ids = (
                Chapter.objects.filter(name__iexact=chapter_key)
                .exclude(owasp_repository__isnull=True)
                .values_list("owasp_repository_id", flat=True)
            )
            queryset = queryset.filter(github_repository__in=chapter_repo_ids)

        if time_range:
            queryset = cls.filter_time_range(queryset, time_range)

        return queryset

    @classmethod
    def filter_time_range(cls, queryset, time_range: str):
        """Filter queryset by time range."""
        if not time_range or time_range.lower() in ("all", "all_time"):
            return queryset

        if delta := cls.TIME_RANGES.get(time_range):
            return queryset.filter(occurred_at__gte=timezone.now() - delta)

        return queryset

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
