"""Dataloaders for issues."""

from collections import defaultdict

from django.db.models import Count, F, Prefetch, Window
from django.db.models.functions import RowNumber
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_result_by_keys, get_results_by_keys
from apps.github.models.issue import Issue
from apps.owasp.models.project import Project

RECENT_ISSUES_LIMIT = 5
ISSUES_BY_REPOSITORY_ID_LOADER = "issues_by_repository_id"
ISSUES_COUNT_BY_PROJECT_ID = "issues_count_by_project_id"
OPEN_ISSUES_COUNT_BY_PROJECT_ID = "open_issues_count_by_project_id"
RECENT_ISSUES_BY_PROJECT_ID = "recent_issues_by_project_id"


async def load_recent_issues_by_project_id(
    keys: list[tuple[int, int]],
) -> list[list[Issue]]:
    """Batch-load recent issues across the given projects' repositories."""
    if not keys:
        return []

    project_ids = [key[0] for key in keys]
    limit = keys[0][1]

    issues = (
        Issue.objects.filter(repository__project__in=project_ids)
        .prefetch_related(
            Prefetch(
                "repository__project_set",
                queryset=Project.objects.filter(pk__in=project_ids).only("pk"),
                to_attr="prefetched_projects",
            ),
        )
        .order_by("-created_at")
        .distinct()
    )

    mapping: dict[int, list[Issue]] = defaultdict(list)
    async for issue in issues:
        for project in issue.repository.prefetched_projects:
            if len(mapping[project.pk]) < limit:
                mapping[project.pk].append(issue)

    return [mapping.get(project_id, []) for project_id in project_ids]


async def load_issues_by_repository_id(
    keys: list[tuple[int, int]],
) -> list[list[Issue]]:
    """Batch-load recent issues for the given repository IDs."""
    if not keys:
        return []

    repository_ids = [key[0] for key in keys]
    limit = keys[0][1]

    issues = (
        Issue.objects.filter(repository_id__in=repository_ids)
        .annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("repository_id")],
                order_by=F("created_at").desc(),
            )
        )
        .filter(row_number__lte=limit)
        .order_by("repository_id", "-created_at")
    )

    return await get_results_by_keys(issues, repository_ids, key_field="repository_id")


async def load_open_issues_count_by_project_id(project_ids: list[int]) -> list[int]:
    """Batch-load open issues count for the given project IDs in a single query."""
    projects = Project.objects.filter(pk__in=project_ids).only("pk", "open_issues_count")
    return [
        result or 0
        for result in await get_result_by_keys(
            projects, project_ids, key_field="pk", value_field="open_issues_count"
        )
    ]


async def load_issues_count_by_project_id(project_ids: list[int]) -> list[int]:
    """Batch-load open issues count for the given project IDs in a single query."""
    projects = Project.objects.filter(pk__in=project_ids).annotate(
        items_count=Count("repositories__issues"),
    )
    return [
        result or 0
        for result in await get_result_by_keys(
            projects, project_ids, key_field="pk", value_field="items_count"
        )
    ]


def get_issue_loaders() -> dict[str, object]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        ISSUES_BY_REPOSITORY_ID_LOADER: DataLoader[tuple[int, int], list[Issue]](
            load_fn=load_issues_by_repository_id,
        ),
        ISSUES_COUNT_BY_PROJECT_ID: DataLoader[int, int](
            load_fn=load_issues_count_by_project_id,
        ),
        OPEN_ISSUES_COUNT_BY_PROJECT_ID: DataLoader[int, int](
            load_fn=load_open_issues_count_by_project_id,
        ),
        RECENT_ISSUES_BY_PROJECT_ID: DataLoader[tuple[int, int], list[Issue]](
            load_fn=load_recent_issues_by_project_id,
        ),
    }
