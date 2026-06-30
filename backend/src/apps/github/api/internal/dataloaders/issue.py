"""Dataloaders for issues."""

from django.db.models import F, Window
from django.db.models.functions import RowNumber
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_results_by_keys
from apps.github.models.issue import Issue

RECENT_ISSUES_LIMIT = 5
ISSUES_BY_REPOSITORY_ID_LOADER = "issues_by_repository_id"


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


def get_issue_loaders() -> dict[str, DataLoader[tuple[int, int], list[Issue]]]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        ISSUES_BY_REPOSITORY_ID_LOADER: DataLoader[tuple[int, int], list[Issue]](
            load_fn=load_issues_by_repository_id,
        ),
    }
