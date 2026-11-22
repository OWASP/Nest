"""OWASP activity event GraphQL queries."""

import strawberry
import strawberry_django

from apps.common.utils import normalize_limit
from apps.owasp.api.internal.nodes.activity_event import (
    ActivityEventNode,
    ActivityEventStatsNode,
    PaginatedActivityEvents,
)
from apps.owasp.models.activity_event import ActivityEvent

PAGE_SIZE = 20


@strawberry.type
class ActivityEventQuery:
    """Activity event queries."""

    @strawberry_django.field
    def activity_events(
        self,
        *,
        activity_type: str | None = None,
        github_user: str | None = None,
        project_key: str | None = None,
        chapter_key: str | None = None,
        time_range: str | None = None,
        include_bots: bool = False,
        order: str = "desc",
        page: int = 1,
        limit: int = PAGE_SIZE,
    ) -> PaginatedActivityEvents:
        """Resolve activity events with optional filtering and pagination."""
        normalized_limit = normalize_limit(limit, ActivityEvent.MAX_LIMIT) or PAGE_SIZE
        page = max(1, page)

        if order not in ActivityEvent.VALID_ORDER_VALUES:
            order = "desc"

        order_clauses = ("occurred_at", "pk") if order == "asc" else ("-occurred_at", "-pk")

        queryset = ActivityEvent.base_queryset().order_by(*order_clauses)
        queryset = ActivityEvent.filter_queryset(
            queryset,
            activity_type=activity_type.strip() if activity_type else None,
            chapter_key=chapter_key.strip() if chapter_key else None,
            github_user=github_user.strip() if github_user else None,
            include_bots=include_bots,
            project_key=project_key.strip() if project_key else None,
            time_range=time_range.strip() if time_range else None,
        )

        total_count = queryset.count()
        total_pages = max(1, (total_count + normalized_limit - 1) // normalized_limit)
        page = max(1, min(page, total_pages))
        offset = (page - 1) * normalized_limit

        return PaginatedActivityEvents(
            current_page=page,
            events=list(queryset[offset : offset + normalized_limit]),
            total_count=total_count,
            total_pages=total_pages,
        )

    @strawberry_django.field
    def recent_activity_events(self, limit: int = 10) -> list[ActivityEventNode]:
        """Resolve recent activity events."""
        if (normalized_limit := normalize_limit(limit, ActivityEvent.MAX_LIMIT)) is None:
            return []

        queryset = ActivityEvent.base_queryset().order_by("-occurred_at", "-pk")
        return list(ActivityEvent.exclude_bots(queryset)[:normalized_limit])

    @strawberry_django.field
    def activity_event_stats(self) -> ActivityEventStatsNode:
        """Resolve overall activity event statistics summary."""
        qs = ActivityEvent.exclude_bots(ActivityEvent.objects.all())
        total_activities = qs.count()
        pull_requests = qs.filter(
            activity_type__in=[
                ActivityEvent.ActivityType.PR_CLOSED,
                ActivityEvent.ActivityType.PR_MERGED,
                ActivityEvent.ActivityType.PR_OPENED,
            ]
        ).count()
        issues = qs.filter(
            activity_type__in=[
                ActivityEvent.ActivityType.ISSUE_CLOSED,
                ActivityEvent.ActivityType.ISSUE_OPENED,
            ]
        ).count()
        contributors = (
            qs.exclude(github_user__isnull=True).values("github_user_id").distinct().count()
        )
        releases = qs.filter(activity_type=ActivityEvent.ActivityType.RELEASE_PUBLISHED).count()
        active_repos = qs.values("github_repository_id").distinct().count()

        return ActivityEventStatsNode(
            active_repos=active_repos,
            contributors=contributors,
            issues=issues,
            pull_requests=pull_requests,
            releases=releases,
            total_activities=total_activities,
        )
