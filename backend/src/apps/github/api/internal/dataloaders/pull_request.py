"""Dataloaders for pull requests."""

from django.db.models import F, Window
from django.db.models.functions import RowNumber
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_results_by_keys
from apps.github.models.pull_request import PullRequest

PULL_REQUESTS_BY_ISSUE_ID_LOADER = "pull_requests_by_issue_id"
RECENT_PULL_REQUESTS_BY_PROJECT_ID_LOADER = "recent_pull_requests_by_project_id"


async def load_pull_requests_by_issue_id(
    keys: list[tuple[int, int, int]],
) -> list[list[PullRequest]]:
    """Batch-load paginated pull requests for the given issue IDs."""
    if not keys:
        return []

    issue_ids = [key[0] for key in keys]
    limit = keys[0][1]
    offset = keys[0][2]

    pull_requests = (
        PullRequest.objects.filter(related_issues__id__in=issue_ids)
        .annotate(
            issue_id=F("related_issues__id"),
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("issue_id")],
                order_by=F("created_at").desc(),
            ),
        )
        .filter(row_number__gt=offset, row_number__lte=offset + limit)
        .order_by("issue_id", "-created_at")
    )

    return await get_results_by_keys(pull_requests, issue_ids, key_field="issue_id")


async def load_recent_pull_requests_by_project_id(
    keys: list[tuple[int, int]],
) -> list[list[PullRequest]]:
    """Batch-load recent pull requests across the given projects' repositories."""
    if not keys:
        return []

    project_ids = [key[0] for key in keys]
    limit = keys[0][1]

    pull_requests = (
        PullRequest.objects.filter(repository__project__in=project_ids)
        .annotate(
            project_id=F("repository__project"),
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("project_id")],
                order_by=F("created_at").desc(),
            ),
        )
        .filter(row_number__lte=limit)
        .order_by("project_id", "-created_at")
    )

    return await get_results_by_keys(pull_requests, project_ids, key_field="project_id")


def get_pull_request_loaders() -> dict[str, object]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        PULL_REQUESTS_BY_ISSUE_ID_LOADER: DataLoader[tuple[int, int, int], list[PullRequest]](
            load_fn=load_pull_requests_by_issue_id,
        ),
        RECENT_PULL_REQUESTS_BY_PROJECT_ID_LOADER: DataLoader[tuple[int, int], list[PullRequest]](
            load_fn=load_recent_pull_requests_by_project_id
        ),
    }
