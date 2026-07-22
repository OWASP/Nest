"""Dataloaders for pull requests."""

from django.db.models import F, Window
from django.db.models.functions import RowNumber
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_results_by_keys
from apps.github.models.pull_request import PullRequest

RECENT_PULL_REQUESTS_BY_PROJECT_ID = "recent_pull_requests_by_project_id"


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
        RECENT_PULL_REQUESTS_BY_PROJECT_ID: DataLoader[tuple[int, int], list[PullRequest]](
            load_fn=load_recent_pull_requests_by_project_id
        ),
    }
