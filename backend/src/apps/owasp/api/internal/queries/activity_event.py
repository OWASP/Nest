"""OWASP activity event GraphQL queries."""

import strawberry
import strawberry_django

from apps.common.utils import normalize_limit
from apps.owasp.api.internal.nodes.activity_event import ActivityEventNode, PaginatedActivityEvents
from apps.owasp.models.activity_event import ActivityEvent
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.project import Project

MAX_LIMIT = 1000
PAGE_SIZE = 20


@strawberry.type
class ActivityEventQuery:
    """Activity event queries."""

    @strawberry_django.field
    def activity_events(
        self,
        *,
        activity_type: str | None = None,
        github_user_login: str | None = None,
        project_key: str | None = None,
        chapter_key: str | None = None,
        time_range: str | None = None,
        include_bots: bool = False,
        order: str = "desc",
        page: int = 1,
        limit: int = PAGE_SIZE,
    ) -> PaginatedActivityEvents:
        """Resolve activity events with optional filtering and pagination."""
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            normalized_limit = PAGE_SIZE

        if page < 1:
            return PaginatedActivityEvents(current_page=1, events=[], total_pages=1)

        if order not in {"asc", "desc"}:
            return PaginatedActivityEvents(current_page=1, events=[], total_pages=1)

        order_clauses = ("occurred_at", "pk") if order == "asc" else ("-occurred_at", "-pk")

        queryset = (
            ActivityEvent.objects.select_related(
                "github_user",
                "github_repository",
            )
            .prefetch_related(
                "source_object",
            )
            .order_by(*order_clauses)
        )

        if not include_bots:
            queryset = ActivityEvent.exclude_bots(queryset)

        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)

        if github_user_login and (cleaned := github_user_login.strip()):
            queryset = queryset.filter(github_user__login__icontains=cleaned)

        if project_key and (cleaned := project_key.strip()):
            project_repo_ids = Project.objects.filter(
                key__icontains=cleaned,
            ).values_list("repositories", flat=True)
            queryset = queryset.filter(github_repository__in=project_repo_ids)

        if chapter_key and (cleaned := chapter_key.strip()):
            chapter_repo_ids = (
                Chapter.objects.filter(
                    key__icontains=cleaned,
                )
                .exclude(
                    owasp_repository__isnull=True,
                )
                .values_list("owasp_repository_id", flat=True)
            )
            queryset = queryset.filter(github_repository__in=chapter_repo_ids)

        if time_range and (cleaned := time_range.strip()):
            queryset = ActivityEvent.filter_time_range(queryset, cleaned)

        total_count = queryset.count()
        total_pages = max(1, (total_count + normalized_limit - 1) // normalized_limit)
        page = max(1, min(page, total_pages))
        offset = (page - 1) * normalized_limit

        return PaginatedActivityEvents(
            current_page=page,
            events=list(queryset[offset : offset + normalized_limit]),
            total_pages=total_pages,
        )

    @strawberry_django.field
    def recent_activity_events(self, limit: int = 10) -> list[ActivityEventNode]:
        """Resolve recent activity events."""
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        queryset = (
            ActivityEvent.objects.select_related(
                "github_user",
                "github_repository",
            )
            .prefetch_related(
                "source_object",
            )
            .order_by("-occurred_at", "-pk")
        )

        return list(ActivityEvent.exclude_bots(queryset)[:normalized_limit])
